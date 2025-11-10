"""
Semantic Search Engine for Umbrella Company Matching
Uses AWS Titan embeddings for intelligent fuzzy matching

Hybrid search strategy:
1. Exact match (fastest)
2. Semantic search (intelligent)
3. Fuzzy fallback (robust)
"""

import json
import math
from typing import Dict, List, Optional, Tuple
from decimal import Decimal

print("[SEMANTIC_SEARCH] Module load started")

try:
    import boto3
    from botocore.exceptions import ClientError
    print("[SEMANTIC_SEARCH] boto3 imported successfully")
except ImportError as e:
    print(f"[SEMANTIC_SEARCH] Warning: boto3 not available: {e}")
    boto3 = None
    ClientError = Exception


class SemanticSearchEngine:
    """
    AWS Titan-based semantic search for umbrella matching

    Features:
    - Generate embeddings using Titan v2
    - Calculate cosine similarity
    - Hybrid search with confidence scoring
    - In-memory caching for performance
    """

    # Similarity thresholds for matching confidence
    THRESHOLDS = {
        'EXACT_SEMANTIC': 0.95,      # Nearly identical (typo only)
        'HIGH_CONFIDENCE': 0.90,     # Strong match (abbreviation, reordering)
        'MEDIUM_CONFIDENCE': 0.85,   # Good match (synonym, variation)
        'LOW_CONFIDENCE': 0.80,      # Questionable match (manual review)
    }

    def __init__(
        self,
        region_name: str = 'us-east-1',
        model_id: str = 'amazon.titan-embed-text-v2:0',
        embedding_dimension: int = 1024
    ):
        """
        Initialize semantic search engine

        Args:
            region_name: AWS region for Bedrock
            model_id: Titan embedding model ID
            embedding_dimension: Embedding vector dimension (256/512/1024)
        """
        print(f"[SEMANTIC_SEARCH] Initializing with model={model_id}, dimension={embedding_dimension}")

        self.model_id = model_id
        self.embedding_dimension = embedding_dimension
        self.region_name = region_name

        # Initialize Bedrock client
        if boto3:
            try:
                self.bedrock_runtime = boto3.client(
                    'bedrock-runtime',
                    region_name=region_name
                )
                self.bedrock_available = True
                print(f"[SEMANTIC_SEARCH] Bedrock client initialized successfully")
            except Exception as e:
                print(f"[SEMANTIC_SEARCH] Warning: Could not initialize Bedrock client: {e}")
                self.bedrock_runtime = None
                self.bedrock_available = False
        else:
            self.bedrock_runtime = None
            self.bedrock_available = False

        # In-memory cache for embeddings
        self.embedding_cache = {}
        print(f"[SEMANTIC_SEARCH] Initialization complete")

    def generate_embedding(self, text: str, use_cache: bool = True) -> Optional[List[float]]:
        """
        Generate embedding for text using AWS Titan

        Args:
            text: Input text to embed
            use_cache: Use cached embedding if available

        Returns:
            List of floats (embedding vector) or None if failed
        """
        if not text or not isinstance(text, str):
            print(f"[SEMANTIC_SEARCH] Invalid input text: {text}")
            return None

        # Normalize text for caching
        text_normalized = text.lower().strip()

        # Check cache
        if use_cache and text_normalized in self.embedding_cache:
            print(f"[SEMANTIC_SEARCH] Cache hit for: {text_normalized}")
            return self.embedding_cache[text_normalized]

        # Check if Bedrock is available
        if not self.bedrock_available or not self.bedrock_runtime:
            print(f"[SEMANTIC_SEARCH] Bedrock not available, cannot generate embedding")
            return None

        try:
            print(f"[SEMANTIC_SEARCH] Generating embedding for: {text}")

            # Prepare request body
            body = json.dumps({
                "inputText": text,
                "dimensions": self.embedding_dimension,
                "normalize": True  # Normalize for cosine similarity
            })

            # Invoke Bedrock model
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=body,
                contentType='application/json',
                accept='application/json'
            )

            # Parse response
            response_body = json.loads(response['body'].read())
            embedding = response_body.get('embedding')

            if not embedding or len(embedding) != self.embedding_dimension:
                print(f"[SEMANTIC_SEARCH] Invalid embedding: length={len(embedding) if embedding else 0}")
                return None

            # Cache the result
            self.embedding_cache[text_normalized] = embedding
            print(f"[SEMANTIC_SEARCH] Embedding generated successfully, cached")

            return embedding

        except ClientError as e:
            print(f"[SEMANTIC_SEARCH] Bedrock API error: {e}")
            return None
        except Exception as e:
            print(f"[SEMANTIC_SEARCH] Unexpected error generating embedding: {e}")
            return None

    def calculate_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score (0.0 - 1.0), or 0.0 if error
        """
        if not embedding1 or not embedding2:
            print(f"[SEMANTIC_SEARCH] Invalid embeddings provided")
            return 0.0

        if len(embedding1) != len(embedding2):
            print(f"[SEMANTIC_SEARCH] Embedding dimension mismatch: {len(embedding1)} vs {len(embedding2)}")
            return 0.0

        try:
            # Calculate cosine similarity
            dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
            magnitude1 = math.sqrt(sum(a * a for a in embedding1))
            magnitude2 = math.sqrt(sum(b * b for b in embedding2))

            if magnitude1 == 0 or magnitude2 == 0:
                print(f"[SEMANTIC_SEARCH] Zero magnitude vector")
                return 0.0

            similarity = dot_product / (magnitude1 * magnitude2)

            # Clamp to [0, 1] range (handle floating point errors)
            similarity = max(0.0, min(1.0, similarity))

            print(f"[SEMANTIC_SEARCH] Cosine similarity: {similarity:.4f}")
            return similarity

        except Exception as e:
            print(f"[SEMANTIC_SEARCH] Error calculating similarity: {e}")
            return 0.0

    def find_best_umbrella_match(
        self,
        input_name: str,
        umbrella_list: List[Dict],
        threshold: float = 0.85,
        use_semantic: bool = True
    ) -> Optional[Dict]:
        """
        Find best matching umbrella using hybrid search strategy

        Search tiers:
        1. Exact code match (GSI1 query)
        2. Semantic embedding similarity
        3. Fuzzy string matching (fallback)

        Args:
            input_name: Umbrella name/code from file
            umbrella_list: List of umbrella dicts from DynamoDB
            threshold: Minimum similarity threshold (0.0 - 1.0)
            use_semantic: Enable semantic search tier

        Returns:
            Match result dict with confidence or None
        """
        print(f"[SEMANTIC_SEARCH] Finding match for: {input_name}")
        print(f"[SEMANTIC_SEARCH] Searching {len(umbrella_list)} umbrellas, threshold={threshold}")

        if not input_name or not isinstance(input_name, str):
            print(f"[SEMANTIC_SEARCH] Invalid input_name")
            return None

        if not umbrella_list:
            print(f"[SEMANTIC_SEARCH] Empty umbrella list")
            return None

        # Normalize input
        input_normalized = input_name.upper().strip()

        # TIER 1: EXACT CODE MATCH
        print(f"[SEMANTIC_SEARCH] Tier 1: Exact match search")
        for umbrella in umbrella_list:
            umbrella_code = umbrella.get('UmbrellaCode', '').upper()
            if umbrella_code == input_normalized:
                print(f"[SEMANTIC_SEARCH] EXACT MATCH: {umbrella_code}")
                return {
                    'match_type': 'EXACT',
                    'umbrella': umbrella,
                    'confidence': 1.0,
                    'similarity': 1.0,
                    'searched_name': input_name,
                    'matched_name': umbrella.get('Name'),
                    'tier': 'EXACT'
                }

        # TIER 2: SEMANTIC SEARCH
        if use_semantic and self.bedrock_available:
            print(f"[SEMANTIC_SEARCH] Tier 2: Semantic search")

            # Generate embedding for input
            input_embedding = self.generate_embedding(input_name)

            if input_embedding:
                best_match = None
                best_similarity = 0.0

                for umbrella in umbrella_list:
                    # Get or generate umbrella embedding
                    umbrella_embedding = self._get_umbrella_embedding(umbrella)

                    if not umbrella_embedding:
                        continue

                    # Calculate similarity
                    similarity = self.calculate_similarity(input_embedding, umbrella_embedding)

                    umbrella_name = umbrella.get('Name', 'Unknown')
                    print(f"[SEMANTIC_SEARCH] Similarity with '{umbrella_name}': {similarity:.4f}")

                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = umbrella

                # Check if best match exceeds threshold
                if best_similarity >= threshold:
                    confidence_tier = self._get_confidence_tier(best_similarity)
                    print(f"[SEMANTIC_SEARCH] SEMANTIC MATCH: similarity={best_similarity:.4f}, tier={confidence_tier}")

                    return {
                        'match_type': 'SEMANTIC',
                        'umbrella': best_match,
                        'confidence': best_similarity,
                        'similarity': best_similarity,
                        'searched_name': input_name,
                        'matched_name': best_match.get('Name'),
                        'tier': confidence_tier
                    }
                else:
                    print(f"[SEMANTIC_SEARCH] Best similarity {best_similarity:.4f} below threshold {threshold}")
            else:
                print(f"[SEMANTIC_SEARCH] Failed to generate input embedding, skipping semantic search")
        else:
            print(f"[SEMANTIC_SEARCH] Semantic search disabled or unavailable")

        # TIER 3: Return None (fuzzy fallback handled by caller)
        print(f"[SEMANTIC_SEARCH] No match found")
        return None

    def _get_umbrella_embedding(self, umbrella: Dict) -> Optional[List[float]]:
        """
        Get embedding for umbrella (from stored field or generate)

        Args:
            umbrella: Umbrella dict from DynamoDB

        Returns:
            Embedding vector or None
        """
        # Check if umbrella has stored embedding
        stored_embedding = umbrella.get('NameEmbedding')

        if stored_embedding and isinstance(stored_embedding, list):
            # Convert Decimal to float if needed (DynamoDB stores as Decimal)
            if stored_embedding and isinstance(stored_embedding[0], Decimal):
                stored_embedding = [float(x) for x in stored_embedding]

            if len(stored_embedding) == self.embedding_dimension:
                print(f"[SEMANTIC_SEARCH] Using stored embedding for: {umbrella.get('Name')}")
                return stored_embedding

        # Generate embedding on-the-fly
        umbrella_name = umbrella.get('Name')
        if not umbrella_name:
            return None

        print(f"[SEMANTIC_SEARCH] Generating embedding for: {umbrella_name}")
        return self.generate_embedding(umbrella_name)

    def _get_confidence_tier(self, similarity: float) -> str:
        """
        Get confidence tier for similarity score

        Args:
            similarity: Cosine similarity score (0.0 - 1.0)

        Returns:
            Confidence tier string
        """
        if similarity >= self.THRESHOLDS['EXACT_SEMANTIC']:
            return 'EXACT_SEMANTIC'
        elif similarity >= self.THRESHOLDS['HIGH_CONFIDENCE']:
            return 'HIGH_CONFIDENCE'
        elif similarity >= self.THRESHOLDS['MEDIUM_CONFIDENCE']:
            return 'MEDIUM_CONFIDENCE'
        elif similarity >= self.THRESHOLDS['LOW_CONFIDENCE']:
            return 'LOW_CONFIDENCE'
        else:
            return 'NO_MATCH'

    def preload_umbrella_embeddings(self, umbrellas: List[Dict]) -> int:
        """
        Pre-generate and cache embeddings for all umbrellas

        Args:
            umbrellas: List of umbrella dicts

        Returns:
            Number of embeddings successfully generated
        """
        print(f"[SEMANTIC_SEARCH] Pre-loading embeddings for {len(umbrellas)} umbrellas")

        count = 0
        for umbrella in umbrellas:
            umbrella_name = umbrella.get('Name')
            if not umbrella_name:
                continue

            embedding = self.generate_embedding(umbrella_name, use_cache=True)
            if embedding:
                count += 1

        print(f"[SEMANTIC_SEARCH] Pre-loaded {count}/{len(umbrellas)} embeddings")
        return count

    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'cache_size': len(self.embedding_cache),
            'cached_texts': list(self.embedding_cache.keys()),
            'bedrock_available': self.bedrock_available
        }


print("[SEMANTIC_SEARCH] Module load complete")
