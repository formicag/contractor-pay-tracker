#!/usr/bin/env python3
"""
Migration Script: Generate Embeddings for Existing Umbrellas

This script:
1. Queries all umbrella companies from DynamoDB
2. Generates embeddings using AWS Titan
3. Updates umbrella items with NameEmbedding field
4. Verifies integrity

Usage:
    python generate_umbrella_embeddings.py [--table-name TABLE_NAME] [--region REGION] [--dry-run]

Requirements:
    - AWS credentials configured
    - Bedrock access enabled
    - DynamoDB table exists
"""

import argparse
import sys
import json
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Optional

# Add common layer to path
sys.path.insert(0, '../layers/common/python')

try:
    import boto3
    from botocore.exceptions import ClientError
    from common.semantic_search import SemanticSearchEngine
    print("[MIGRATION] Successfully imported required modules")
except ImportError as e:
    print(f"[MIGRATION] Error: Failed to import required modules: {e}")
    print("[MIGRATION] Please ensure you're running from the scripts directory")
    sys.exit(1)


class UmbrellaEmbeddingMigration:
    """Handles migration of umbrella embeddings"""

    def __init__(
        self,
        table_name: str,
        region: str = 'us-east-1',
        dry_run: bool = False
    ):
        """
        Initialize migration

        Args:
            table_name: DynamoDB table name
            region: AWS region
            dry_run: If True, don't write to DynamoDB
        """
        self.table_name = table_name
        self.region = region
        self.dry_run = dry_run

        print(f"[MIGRATION] Initializing migration")
        print(f"[MIGRATION] Table: {table_name}, Region: {region}, Dry run: {dry_run}")

        # Initialize AWS clients
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(table_name)

        # Initialize semantic search engine
        self.semantic_engine = SemanticSearchEngine(region_name=region)

        # Statistics
        self.stats = {
            'total_umbrellas': 0,
            'embeddings_generated': 0,
            'embeddings_updated': 0,
            'errors': 0,
            'skipped': 0
        }

    def fetch_all_umbrellas(self) -> List[Dict]:
        """
        Fetch all umbrella companies from DynamoDB

        Returns:
            List of umbrella dicts
        """
        print(f"[MIGRATION] Fetching all umbrellas from table: {self.table_name}")

        try:
            # Query using GSI1 for active umbrellas
            response = self.table.query(
                IndexName='GSI1',
                KeyConditionExpression='GSI1PK = :pk',
                ExpressionAttributeValues={':pk': 'UMBRELLAS'}
            )

            umbrellas = response.get('Items', [])
            print(f"[MIGRATION] Found {len(umbrellas)} umbrellas")

            self.stats['total_umbrellas'] = len(umbrellas)
            return umbrellas

        except ClientError as e:
            print(f"[MIGRATION] Error fetching umbrellas: {e}")
            raise

    def generate_embedding_for_umbrella(self, umbrella: Dict) -> Optional[List[float]]:
        """
        Generate embedding for umbrella name

        Args:
            umbrella: Umbrella dict

        Returns:
            Embedding vector or None if failed
        """
        umbrella_name = umbrella.get('Name')
        umbrella_id = umbrella.get('UmbrellaID')

        if not umbrella_name:
            print(f"[MIGRATION] Warning: Umbrella {umbrella_id} has no Name field, skipping")
            self.stats['skipped'] += 1
            return None

        print(f"[MIGRATION] Generating embedding for: {umbrella_name} ({umbrella_id})")

        try:
            embedding = self.semantic_engine.generate_embedding(
                umbrella_name,
                use_cache=False  # Don't use cache for migration
            )

            if embedding and len(embedding) == 1024:
                print(f"[MIGRATION] Successfully generated embedding (dimension: {len(embedding)})")
                self.stats['embeddings_generated'] += 1
                return embedding
            else:
                print(f"[MIGRATION] Warning: Invalid embedding generated for {umbrella_name}")
                self.stats['errors'] += 1
                return None

        except Exception as e:
            print(f"[MIGRATION] Error generating embedding for {umbrella_name}: {e}")
            self.stats['errors'] += 1
            return None

    def update_umbrella_with_embedding(
        self,
        umbrella: Dict,
        embedding: List[float]
    ) -> bool:
        """
        Update umbrella item with embedding

        Args:
            umbrella: Umbrella dict
            embedding: Embedding vector

        Returns:
            True if successful
        """
        umbrella_id = umbrella.get('UmbrellaID')
        pk = umbrella.get('PK')
        sk = umbrella.get('SK')

        if not pk or not sk:
            print(f"[MIGRATION] Warning: Umbrella {umbrella_id} missing PK/SK")
            return False

        if self.dry_run:
            print(f"[MIGRATION] [DRY RUN] Would update umbrella {umbrella_id} with embedding")
            self.stats['embeddings_updated'] += 1
            return True

        try:
            # Convert embedding to list of Decimals for DynamoDB
            embedding_decimal = [Decimal(str(float(x))) for x in embedding]

            # Update item
            timestamp = datetime.utcnow().isoformat() + 'Z'

            self.table.update_item(
                Key={'PK': pk, 'SK': sk},
                UpdateExpression='SET NameEmbedding = :emb, EmbeddingModel = :model, EmbeddingVersion = :ver, EmbeddingGeneratedAt = :time',
                ExpressionAttributeValues={
                    ':emb': embedding_decimal,
                    ':model': 'amazon.titan-embed-text-v2:0',
                    ':ver': 'v1',
                    ':time': timestamp
                }
            )

            print(f"[MIGRATION] Successfully updated umbrella {umbrella_id}")
            self.stats['embeddings_updated'] += 1
            return True

        except ClientError as e:
            print(f"[MIGRATION] Error updating umbrella {umbrella_id}: {e}")
            self.stats['errors'] += 1
            return False

    def verify_embeddings(self, umbrellas: List[Dict]) -> Dict:
        """
        Verify that embeddings were stored correctly

        Args:
            umbrellas: List of umbrella dicts (original, before update)

        Returns:
            Verification results dict
        """
        print(f"[MIGRATION] Verifying embeddings for {len(umbrellas)} umbrellas")

        verified = 0
        failed = 0

        for umbrella in umbrellas:
            umbrella_id = umbrella.get('UmbrellaID')
            pk = umbrella.get('PK')
            sk = umbrella.get('SK')

            try:
                # Re-fetch item
                response = self.table.get_item(Key={'PK': pk, 'SK': sk})
                updated_umbrella = response.get('Item')

                if not updated_umbrella:
                    print(f"[MIGRATION] Verification failed: {umbrella_id} not found")
                    failed += 1
                    continue

                # Check if embedding exists
                embedding = updated_umbrella.get('NameEmbedding')
                if embedding and len(embedding) == 1024:
                    verified += 1
                else:
                    print(f"[MIGRATION] Verification failed: {umbrella_id} has invalid/missing embedding")
                    failed += 1

            except Exception as e:
                print(f"[MIGRATION] Verification error for {umbrella_id}: {e}")
                failed += 1

        results = {
            'verified': verified,
            'failed': failed,
            'total': len(umbrellas)
        }

        print(f"[MIGRATION] Verification complete: {verified}/{len(umbrellas)} successful")
        return results

    def run(self) -> bool:
        """
        Run the migration

        Returns:
            True if successful
        """
        print(f"[MIGRATION] ========================================")
        print(f"[MIGRATION] Starting Umbrella Embedding Migration")
        print(f"[MIGRATION] ========================================")
        print(f"[MIGRATION] Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print()

        try:
            # Step 1: Fetch all umbrellas
            umbrellas = self.fetch_all_umbrellas()

            if not umbrellas:
                print("[MIGRATION] No umbrellas found to migrate")
                return True

            print()

            # Step 2: Generate and update embeddings
            print(f"[MIGRATION] Generating embeddings for {len(umbrellas)} umbrellas...")
            print()

            for idx, umbrella in enumerate(umbrellas, start=1):
                umbrella_name = umbrella.get('Name', 'Unknown')
                print(f"[MIGRATION] Processing {idx}/{len(umbrellas)}: {umbrella_name}")

                # Generate embedding
                embedding = self.generate_embedding_for_umbrella(umbrella)

                if embedding:
                    # Update DynamoDB
                    success = self.update_umbrella_with_embedding(umbrella, embedding)
                    if not success:
                        print(f"[MIGRATION] Warning: Failed to update {umbrella_name}")

                print()

            # Step 3: Verify (if not dry run)
            if not self.dry_run:
                print("[MIGRATION] Verifying embeddings...")
                verification = self.verify_embeddings(umbrellas)
                print()

            # Step 4: Print summary
            print(f"[MIGRATION] ========================================")
            print(f"[MIGRATION] Migration Complete")
            print(f"[MIGRATION] ========================================")
            print(f"[MIGRATION] Total umbrellas: {self.stats['total_umbrellas']}")
            print(f"[MIGRATION] Embeddings generated: {self.stats['embeddings_generated']}")
            print(f"[MIGRATION] Embeddings updated: {self.stats['embeddings_updated']}")
            print(f"[MIGRATION] Skipped: {self.stats['skipped']}")
            print(f"[MIGRATION] Errors: {self.stats['errors']}")

            if not self.dry_run:
                print(f"[MIGRATION] Verified: {verification['verified']}/{verification['total']}")

            print(f"[MIGRATION] ========================================")

            # Return success if no errors
            return self.stats['errors'] == 0

        except Exception as e:
            print(f"[MIGRATION] Fatal error during migration: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Generate embeddings for existing umbrella companies'
    )
    parser.add_argument(
        '--table-name',
        default='contractor-pay-tracker',
        help='DynamoDB table name (default: contractor-pay-tracker)'
    )
    parser.add_argument(
        '--region',
        default='us-east-1',
        help='AWS region (default: us-east-1)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Perform dry run without writing to DynamoDB'
    )

    args = parser.parse_args()

    # Confirm if not dry run
    if not args.dry_run:
        print(f"[MIGRATION] WARNING: This will modify DynamoDB table '{args.table_name}'")
        response = input("[MIGRATION] Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("[MIGRATION] Aborted by user")
            sys.exit(0)

    # Run migration
    migration = UmbrellaEmbeddingMigration(
        table_name=args.table_name,
        region=args.region,
        dry_run=args.dry_run
    )

    success = migration.run()

    if success:
        print("[MIGRATION] Migration completed successfully!")
        sys.exit(0)
    else:
        print("[MIGRATION] Migration completed with errors")
        sys.exit(1)


if __name__ == '__main__':
    main()
