"""
Report Generator Lambda Function
Generates comprehensive reports and analytics from pay data
"""

print("[REPORT_GENERATOR] ========================================")
print("[REPORT_GENERATOR] Module loading started")
print("[REPORT_GENERATOR] ========================================")

print("[REPORT_GENERATOR] Importing json")
import json
print(f"[REPORT_GENERATOR] json imported: {json}")

print("[REPORT_GENERATOR] Importing os")
import os
print(f"[REPORT_GENERATOR] os imported: {os}")

print("[REPORT_GENERATOR] Importing csv")
import csv
print(f"[REPORT_GENERATOR] csv imported: {csv}")

print("[REPORT_GENERATOR] Importing io")
import io
print(f"[REPORT_GENERATOR] io imported: {io}")

print("[REPORT_GENERATOR] Importing uuid")
import uuid
print(f"[REPORT_GENERATOR] uuid imported: {uuid}")

print("[REPORT_GENERATOR] Importing datetime from datetime")
from datetime import datetime
print(f"[REPORT_GENERATOR] datetime imported: {datetime}")

print("[REPORT_GENERATOR] Importing Decimal from decimal")
from decimal import Decimal
print(f"[REPORT_GENERATOR] Decimal imported: {Decimal}")

print("[REPORT_GENERATOR] Importing boto3")
import boto3
print(f"[REPORT_GENERATOR] boto3 imported: {boto3}")

print("[REPORT_GENERATOR] Importing from common layer")
print("[REPORT_GENERATOR] Importing StructuredLogger from common.logger")
from common.logger import StructuredLogger
print(f"[REPORT_GENERATOR] StructuredLogger imported: {StructuredLogger}")

print("[REPORT_GENERATOR] Importing DynamoDBClient from common.dynamodb")
from common.dynamodb import DynamoDBClient
print(f"[REPORT_GENERATOR] DynamoDBClient imported: {DynamoDBClient}")

print("[REPORT_GENERATOR] ========================================")
print("[REPORT_GENERATOR] Module loading completed")
print("[REPORT_GENERATOR] ========================================")

print("[REPORT_GENERATOR] About to execute: s3_client = boto3.client('s3')")
s3_client = boto3.client('s3')
print(f"[REPORT_GENERATOR] s3_client created: {s3_client}")

print("[REPORT_GENERATOR] About to execute: dynamodb_client = DynamoDBClient()")
dynamodb_client = DynamoDBClient()
print(f"[REPORT_GENERATOR] dynamodb_client created: {dynamodb_client}")

print("[REPORT_GENERATOR] About to execute: s3_bucket = os.environ.get('S3_BUCKET_NAME')")
s3_bucket = os.environ.get('S3_BUCKET_NAME')
print(f"[REPORT_GENERATOR] s3_bucket from environment: {s3_bucket}")


def lambda_handler(event, context):
    """
    Generate reports from pay data
    Supports multiple report types: summary, detailed, contractor-specific, period-specific
    """
    print("[REPORT_GENERATOR] ========================================")
    print("[REPORT_GENERATOR] lambda_handler() invoked")
    print("[REPORT_GENERATOR] ========================================")
    print(f"[REPORT_GENERATOR] event parameter: {event}")
    print(f"[REPORT_GENERATOR] context parameter: {context}")
    print(f"[REPORT_GENERATOR] context.aws_request_id: {context.aws_request_id}")

    print("[REPORT_GENERATOR] Creating StructuredLogger")
    logger = StructuredLogger("report-generator", context.aws_request_id)
    print(f"[REPORT_GENERATOR] logger created: {logger}")

    print("[REPORT_GENERATOR] Logging info message: Report generator invoked")
    logger.info("Report generator invoked", event=event)
    print("[REPORT_GENERATOR] Info message logged")

    try:
        print("[REPORT_GENERATOR] Entering try block")

        print("[REPORT_GENERATOR] About to execute: extract report_type from event")
        report_type = event.get('report_type', 'summary')
        print(f"[REPORT_GENERATOR] report_type: {report_type}")

        print("[REPORT_GENERATOR] About to execute: extract filters from event")
        filters = event.get('filters', {})
        print(f"[REPORT_GENERATOR] filters: {filters}")

        print(f"[REPORT_GENERATOR] About to execute: logger.info 'Generating report' with report_type={report_type}, filters={filters}")
        logger.info("Generating report", report_type=report_type, filters=filters)
        print("[REPORT_GENERATOR] Info message logged")

        print(f"[REPORT_GENERATOR] About to execute: check report_type == 'summary'")
        if report_type == 'summary':
            print("[REPORT_GENERATOR] About to execute: result = generate_summary_report(filters, logger)")
            result = generate_summary_report(filters, logger)
            print(f"[REPORT_GENERATOR] Result from generate_summary_report: {result}")

        print(f"[REPORT_GENERATOR] About to execute: check report_type == 'detailed'")
        elif report_type == 'detailed':
            print("[REPORT_GENERATOR] About to execute: result = generate_detailed_report(filters, logger)")
            result = generate_detailed_report(filters, logger)
            print(f"[REPORT_GENERATOR] Result from generate_detailed_report: {result}")

        print(f"[REPORT_GENERATOR] About to execute: check report_type == 'contractor'")
        elif report_type == 'contractor':
            print("[REPORT_GENERATOR] About to execute: result = generate_contractor_report(filters, logger)")
            result = generate_contractor_report(filters, logger)
            print(f"[REPORT_GENERATOR] Result from generate_contractor_report: {result}")

        print(f"[REPORT_GENERATOR] About to execute: check report_type == 'period'")
        elif report_type == 'period':
            print("[REPORT_GENERATOR] About to execute: result = generate_period_report(filters, logger)")
            result = generate_period_report(filters, logger)
            print(f"[REPORT_GENERATOR] Result from generate_period_report: {result}")

        else:
            print(f"[REPORT_GENERATOR] About to execute: raise ValueError for unknown report_type: {report_type}")
            raise ValueError(f"Unknown report type: {report_type}")

        print("[REPORT_GENERATOR] Converting result to JSON string")
        response_body_json = json.dumps(result)
        print(f"[REPORT_GENERATOR] response_body_json: {response_body_json}")

        print("[REPORT_GENERATOR] Building response")
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': response_body_json
        }
        print(f"[REPORT_GENERATOR] response: {response}")

        print("[REPORT_GENERATOR] Logging success response")
        logger.info("Report generation completed successfully", report_type=report_type)
        print("[REPORT_GENERATOR] Success logged")

        print("[REPORT_GENERATOR] ========================================")
        print("[REPORT_GENERATOR] lambda_handler() returning success response")
        print("[REPORT_GENERATOR] ========================================")
        return response

    except Exception as e:
        print("[REPORT_GENERATOR] !!! EXCEPTION CAUGHT !!!")
        print(f"[REPORT_GENERATOR] Exception type: {type(e)}")
        print(f"[REPORT_GENERATOR] Exception message: {str(e)}")
        print(f"[REPORT_GENERATOR] Exception args: {e.args}")

        print("[REPORT_GENERATOR] Logging error via logger")
        logger.error("Report generation error", error=str(e))
        print("[REPORT_GENERATOR] Error logged")

        print("[REPORT_GENERATOR] Building error response")
        error_response = {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
        print(f"[REPORT_GENERATOR] error_response: {error_response}")
        print("[REPORT_GENERATOR] lambda_handler() returning error response")
        return error_response


def generate_summary_report(filters: dict, logger: StructuredLogger) -> dict:
    """
    Generate summary report with totals and statistics
    """
    print(f"[GENERATE_SUMMARY] About to execute: generate_summary_report with filters={filters}")
    print(f"[GENERATE_SUMMARY] About to execute: logger.info 'Generating summary report'")
    logger.info("Generating summary report", filters=filters)
    print("[GENERATE_SUMMARY] Info message logged")

    print("[GENERATE_SUMMARY] About to execute: extract period_id from filters")
    period_id = filters.get('period_id')
    print(f"[GENERATE_SUMMARY] period_id: {period_id}")

    print("[GENERATE_SUMMARY] About to execute: extract umbrella_id from filters")
    umbrella_id = filters.get('umbrella_id')
    print(f"[GENERATE_SUMMARY] umbrella_id: {umbrella_id}")

    # Query pay records using GSI2 (period-based queries)
    print("[GENERATE_SUMMARY] About to execute: query_records with period_id and umbrella_id")
    records = query_records(period_id=period_id, umbrella_id=umbrella_id, logger=logger)
    print(f"[GENERATE_SUMMARY] Records retrieved: {len(records)} records")

    print("[GENERATE_SUMMARY] About to execute: calculate_statistics from records")
    stats = calculate_statistics(records, logger)
    print(f"[GENERATE_SUMMARY] Statistics calculated: {stats}")

    print("[GENERATE_SUMMARY] About to execute: generate_csv from records and stats")
    csv_data = generate_csv(records, report_type='summary', logger=logger)
    print(f"[GENERATE_SUMMARY] CSV data generated: {len(csv_data)} bytes")

    print("[GENERATE_SUMMARY] About to execute: upload_to_s3 with csv_data")
    s3_key = upload_to_s3(csv_data, report_type='summary', filters=filters, logger=logger)
    print(f"[GENERATE_SUMMARY] S3 upload complete: {s3_key}")

    print("[GENERATE_SUMMARY] About to execute: build result dict")
    result = {
        'report_type': 'summary',
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'filters': filters,
        'statistics': stats,
        's3_bucket': s3_bucket,
        's3_key': s3_key,
        'record_count': len(records)
    }
    print(f"[GENERATE_SUMMARY] Result: {result}")
    print("[GENERATE_SUMMARY] Returning result")
    return result


def generate_detailed_report(filters: dict, logger: StructuredLogger) -> dict:
    """
    Generate detailed report with all pay record details
    """
    print(f"[GENERATE_DETAILED] About to execute: generate_detailed_report with filters={filters}")
    print(f"[GENERATE_DETAILED] About to execute: logger.info 'Generating detailed report'")
    logger.info("Generating detailed report", filters=filters)
    print("[GENERATE_DETAILED] Info message logged")

    print("[GENERATE_DETAILED] About to execute: extract period_id from filters")
    period_id = filters.get('period_id')
    print(f"[GENERATE_DETAILED] period_id: {period_id}")

    print("[GENERATE_DETAILED] About to execute: extract umbrella_id from filters")
    umbrella_id = filters.get('umbrella_id')
    print(f"[GENERATE_DETAILED] umbrella_id: {umbrella_id}")

    print("[GENERATE_DETAILED] About to execute: query_records with period_id and umbrella_id")
    records = query_records(period_id=period_id, umbrella_id=umbrella_id, logger=logger)
    print(f"[GENERATE_DETAILED] Records retrieved: {len(records)} records")

    print("[GENERATE_DETAILED] About to execute: enrich_records with contractor and umbrella details")
    enriched_records = enrich_records(records, logger)
    print(f"[GENERATE_DETAILED] Records enriched: {len(enriched_records)} records")

    print("[GENERATE_DETAILED] About to execute: calculate_statistics from records")
    stats = calculate_statistics(records, logger)
    print(f"[GENERATE_DETAILED] Statistics calculated: {stats}")

    print("[GENERATE_DETAILED] About to execute: generate_csv from enriched_records")
    csv_data = generate_csv(enriched_records, report_type='detailed', logger=logger)
    print(f"[GENERATE_DETAILED] CSV data generated: {len(csv_data)} bytes")

    print("[GENERATE_DETAILED] About to execute: upload_to_s3 with csv_data")
    s3_key = upload_to_s3(csv_data, report_type='detailed', filters=filters, logger=logger)
    print(f"[GENERATE_DETAILED] S3 upload complete: {s3_key}")

    print("[GENERATE_DETAILED] About to execute: build result dict")
    result = {
        'report_type': 'detailed',
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'filters': filters,
        'statistics': stats,
        's3_bucket': s3_bucket,
        's3_key': s3_key,
        'record_count': len(enriched_records)
    }
    print(f"[GENERATE_DETAILED] Result: {result}")
    print("[GENERATE_DETAILED] Returning result")
    return result


def generate_contractor_report(filters: dict, logger: StructuredLogger) -> dict:
    """
    Generate contractor-specific report
    """
    print(f"[GENERATE_CONTRACTOR] About to execute: generate_contractor_report with filters={filters}")
    print(f"[GENERATE_CONTRACTOR] About to execute: logger.info 'Generating contractor report'")
    logger.info("Generating contractor report", filters=filters)
    print("[GENERATE_CONTRACTOR] Info message logged")

    print("[GENERATE_CONTRACTOR] About to execute: extract contractor_id from filters")
    contractor_id = filters.get('contractor_id')
    print(f"[GENERATE_CONTRACTOR] contractor_id: {contractor_id}")

    print("[GENERATE_CONTRACTOR] About to execute: check if not contractor_id")
    if not contractor_id:
        print("[GENERATE_CONTRACTOR] About to execute: raise ValueError for missing contractor_id")
        raise ValueError("contractor_id is required for contractor report")

    # Query using GSI1 (contractor-based queries)
    print("[GENERATE_CONTRACTOR] About to execute: query_records with contractor_id")
    records = query_records(contractor_id=contractor_id, logger=logger)
    print(f"[GENERATE_CONTRACTOR] Records retrieved: {len(records)} records")

    print("[GENERATE_CONTRACTOR] About to execute: get_contractor_details for contractor_id")
    contractor_details = get_contractor_details(contractor_id, logger)
    print(f"[GENERATE_CONTRACTOR] Contractor details: {contractor_details}")

    print("[GENERATE_CONTRACTOR] About to execute: enrich_records with period and umbrella details")
    enriched_records = enrich_records(records, logger)
    print(f"[GENERATE_CONTRACTOR] Records enriched: {len(enriched_records)} records")

    print("[GENERATE_CONTRACTOR] About to execute: calculate_statistics from records")
    stats = calculate_statistics(records, logger)
    print(f"[GENERATE_CONTRACTOR] Statistics calculated: {stats}")

    print("[GENERATE_CONTRACTOR] About to execute: generate_csv from enriched_records")
    csv_data = generate_csv(enriched_records, report_type='contractor', logger=logger)
    print(f"[GENERATE_CONTRACTOR] CSV data generated: {len(csv_data)} bytes")

    print("[GENERATE_CONTRACTOR] About to execute: upload_to_s3 with csv_data")
    s3_key = upload_to_s3(csv_data, report_type='contractor', filters=filters, logger=logger)
    print(f"[GENERATE_CONTRACTOR] S3 upload complete: {s3_key}")

    print("[GENERATE_CONTRACTOR] About to execute: build result dict")
    result = {
        'report_type': 'contractor',
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'filters': filters,
        'contractor': contractor_details,
        'statistics': stats,
        's3_bucket': s3_bucket,
        's3_key': s3_key,
        'record_count': len(enriched_records)
    }
    print(f"[GENERATE_CONTRACTOR] Result: {result}")
    print("[GENERATE_CONTRACTOR] Returning result")
    return result


def generate_period_report(filters: dict, logger: StructuredLogger) -> dict:
    """
    Generate period-specific report
    """
    print(f"[GENERATE_PERIOD] About to execute: generate_period_report with filters={filters}")
    print(f"[GENERATE_PERIOD] About to execute: logger.info 'Generating period report'")
    logger.info("Generating period report", filters=filters)
    print("[GENERATE_PERIOD] Info message logged")

    print("[GENERATE_PERIOD] About to execute: extract period_id from filters")
    period_id = filters.get('period_id')
    print(f"[GENERATE_PERIOD] period_id: {period_id}")

    print("[GENERATE_PERIOD] About to execute: check if not period_id")
    if not period_id:
        print("[GENERATE_PERIOD] About to execute: raise ValueError for missing period_id")
        raise ValueError("period_id is required for period report")

    # Query using GSI2 (period-based queries)
    print("[GENERATE_PERIOD] About to execute: query_records with period_id")
    records = query_records(period_id=period_id, logger=logger)
    print(f"[GENERATE_PERIOD] Records retrieved: {len(records)} records")

    print("[GENERATE_PERIOD] About to execute: get_period_details for period_id")
    period_details = get_period_details(period_id, logger)
    print(f"[GENERATE_PERIOD] Period details: {period_details}")

    print("[GENERATE_PERIOD] About to execute: enrich_records with contractor and umbrella details")
    enriched_records = enrich_records(records, logger)
    print(f"[GENERATE_PERIOD] Records enriched: {len(enriched_records)} records")

    print("[GENERATE_PERIOD] About to execute: calculate_statistics from records")
    stats = calculate_statistics(records, logger)
    print(f"[GENERATE_PERIOD] Statistics calculated: {stats}")

    print("[GENERATE_PERIOD] About to execute: calculate_umbrella_breakdown from records")
    umbrella_breakdown = calculate_umbrella_breakdown(records, logger)
    print(f"[GENERATE_PERIOD] Umbrella breakdown: {umbrella_breakdown}")

    print("[GENERATE_PERIOD] About to execute: generate_csv from enriched_records")
    csv_data = generate_csv(enriched_records, report_type='period', logger=logger)
    print(f"[GENERATE_PERIOD] CSV data generated: {len(csv_data)} bytes")

    print("[GENERATE_PERIOD] About to execute: upload_to_s3 with csv_data")
    s3_key = upload_to_s3(csv_data, report_type='period', filters=filters, logger=logger)
    print(f"[GENERATE_PERIOD] S3 upload complete: {s3_key}")

    print("[GENERATE_PERIOD] About to execute: build result dict")
    result = {
        'report_type': 'period',
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'filters': filters,
        'period': period_details,
        'statistics': stats,
        'umbrella_breakdown': umbrella_breakdown,
        's3_bucket': s3_bucket,
        's3_key': s3_key,
        'record_count': len(enriched_records)
    }
    print(f"[GENERATE_PERIOD] Result: {result}")
    print("[GENERATE_PERIOD] Returning result")
    return result


def query_records(period_id=None, umbrella_id=None, contractor_id=None, logger=None):
    """
    Query pay records from DynamoDB using appropriate GSI
    """
    print(f"[QUERY_RECORDS] About to execute: query_records with period_id={period_id}, umbrella_id={umbrella_id}, contractor_id={contractor_id}")

    print("[QUERY_RECORDS] About to execute: initialize records = []")
    records = []
    print(f"[QUERY_RECORDS] records initialized: {records}")

    print("[QUERY_RECORDS] About to execute: check if contractor_id")
    if contractor_id:
        # Use GSI1 for contractor-based queries
        print(f"[QUERY_RECORDS] About to execute: query GSI1 with contractor_id={contractor_id}")
        print(f"[QUERY_RECORDS] About to execute: logger.info 'Querying by contractor'")
        logger.info("Querying by contractor", contractor_id=contractor_id)
        print("[QUERY_RECORDS] Info message logged")

        print("[QUERY_RECORDS] About to execute: build GSI1PK")
        gsi1pk = f'CONTRACTOR#{contractor_id}'
        print(f"[QUERY_RECORDS] GSI1PK: {gsi1pk}")

        print("[QUERY_RECORDS] About to execute: dynamodb_client.table.query on GSI1")
        response = dynamodb_client.table.query(
            IndexName='GSI1',
            KeyConditionExpression='GSI1PK = :pk',
            FilterExpression='IsActive = :active AND EntityType = :type',
            ExpressionAttributeValues={
                ':pk': gsi1pk,
                ':active': True,
                ':type': 'PayRecord'
            }
        )
        print(f"[QUERY_RECORDS] Query response: {response}")

        print("[QUERY_RECORDS] About to execute: extract Items from response")
        records = response.get('Items', [])
        print(f"[QUERY_RECORDS] Records extracted: {len(records)} records")

    print("[QUERY_RECORDS] About to execute: check if period_id")
    elif period_id:
        # Use GSI2 for period-based queries
        print(f"[QUERY_RECORDS] About to execute: query GSI2 with period_id={period_id}")
        print(f"[QUERY_RECORDS] About to execute: logger.info 'Querying by period'")
        logger.info("Querying by period", period_id=period_id, umbrella_id=umbrella_id)
        print("[QUERY_RECORDS] Info message logged")

        print("[QUERY_RECORDS] About to execute: build GSI2PK")
        gsi2pk = f'PERIOD#{period_id}'
        print(f"[QUERY_RECORDS] GSI2PK: {gsi2pk}")

        print("[QUERY_RECORDS] About to execute: check if umbrella_id")
        if umbrella_id:
            print(f"[QUERY_RECORDS] About to execute: query with umbrella filter, umbrella_id={umbrella_id}")
            print("[QUERY_RECORDS] About to execute: dynamodb_client.table.query on GSI2 with umbrella filter")
            response = dynamodb_client.table.query(
                IndexName='GSI2',
                KeyConditionExpression='GSI2PK = :pk',
                FilterExpression='IsActive = :active AND EntityType = :type AND UmbrellaID = :umbrella',
                ExpressionAttributeValues={
                    ':pk': gsi2pk,
                    ':active': True,
                    ':type': 'PayRecord',
                    ':umbrella': umbrella_id
                }
            )
            print(f"[QUERY_RECORDS] Query response: {response}")
        else:
            print("[QUERY_RECORDS] About to execute: query without umbrella filter")
            print("[QUERY_RECORDS] About to execute: dynamodb_client.table.query on GSI2")
            response = dynamodb_client.table.query(
                IndexName='GSI2',
                KeyConditionExpression='GSI2PK = :pk',
                FilterExpression='IsActive = :active AND EntityType = :type',
                ExpressionAttributeValues={
                    ':pk': gsi2pk,
                    ':active': True,
                    ':type': 'PayRecord'
                }
            )
            print(f"[QUERY_RECORDS] Query response: {response}")

        print("[QUERY_RECORDS] About to execute: extract Items from response")
        records = response.get('Items', [])
        print(f"[QUERY_RECORDS] Records extracted: {len(records)} records")

    else:
        print("[QUERY_RECORDS] About to execute: scan all active pay records")
        print("[QUERY_RECORDS] About to execute: logger.info 'Querying all records'")
        logger.info("Querying all records")
        print("[QUERY_RECORDS] Info message logged")

        print("[QUERY_RECORDS] About to execute: dynamodb_client.table.scan")
        response = dynamodb_client.table.scan(
            FilterExpression='IsActive = :active AND EntityType = :type',
            ExpressionAttributeValues={
                ':active': True,
                ':type': 'PayRecord'
            }
        )
        print(f"[QUERY_RECORDS] Scan response: {response}")

        print("[QUERY_RECORDS] About to execute: extract Items from response")
        records = response.get('Items', [])
        print(f"[QUERY_RECORDS] Records extracted: {len(records)} records")

    print(f"[QUERY_RECORDS] About to execute: logger.info 'Records queried' with count={len(records)}")
    logger.info("Records queried", count=len(records))
    print("[QUERY_RECORDS] Info message logged")

    print(f"[QUERY_RECORDS] Returning {len(records)} records")
    return records


def enrich_records(records, logger):
    """
    Enrich records with contractor and umbrella company details
    """
    print(f"[ENRICH_RECORDS] About to execute: enrich_records with {len(records)} records")
    print(f"[ENRICH_RECORDS] About to execute: logger.info 'Enriching records'")
    logger.info("Enriching records", count=len(records))
    print("[ENRICH_RECORDS] Info message logged")

    print("[ENRICH_RECORDS] About to execute: initialize enriched = []")
    enriched = []
    print(f"[ENRICH_RECORDS] enriched initialized: {enriched}")

    print(f"[ENRICH_RECORDS] About to execute: iterate through {len(records)} records")
    for idx, record in enumerate(records):
        print(f"[ENRICH_RECORDS] About to execute: process record {idx+1}/{len(records)}")

        print(f"[ENRICH_RECORDS] About to execute: copy record dict")
        enriched_record = dict(record)
        print(f"[ENRICH_RECORDS] Record copied")

        # Get contractor details
        print(f"[ENRICH_RECORDS] About to execute: extract ContractorID from record")
        contractor_id = record.get('ContractorID')
        print(f"[ENRICH_RECORDS] ContractorID: {contractor_id}")

        print("[ENRICH_RECORDS] About to execute: check if contractor_id")
        if contractor_id:
            print(f"[ENRICH_RECORDS] About to execute: get_contractor_details for contractor_id={contractor_id}")
            contractor = get_contractor_details(contractor_id, logger)
            print(f"[ENRICH_RECORDS] Contractor details: {contractor}")

            print("[ENRICH_RECORDS] About to execute: add contractor details to enriched_record")
            enriched_record['ContractorName'] = f"{contractor.get('FirstName', '')} {contractor.get('LastName', '')}"
            enriched_record['ContractorJobTitle'] = contractor.get('JobTitle', '')
            print(f"[ENRICH_RECORDS] Contractor details added")

        # Get umbrella details
        print(f"[ENRICH_RECORDS] About to execute: extract UmbrellaID from record")
        umbrella_id = record.get('UmbrellaID')
        print(f"[ENRICH_RECORDS] UmbrellaID: {umbrella_id}")

        print("[ENRICH_RECORDS] About to execute: check if umbrella_id")
        if umbrella_id:
            print(f"[ENRICH_RECORDS] About to execute: get_umbrella_details for umbrella_id={umbrella_id}")
            umbrella = get_umbrella_details(umbrella_id, logger)
            print(f"[ENRICH_RECORDS] Umbrella details: {umbrella}")

            print("[ENRICH_RECORDS] About to execute: add umbrella details to enriched_record")
            enriched_record['UmbrellaName'] = umbrella.get('LegalName', '')
            enriched_record['UmbrellaCode'] = umbrella.get('ShortCode', '')
            print(f"[ENRICH_RECORDS] Umbrella details added")

        # Get period details
        print(f"[ENRICH_RECORDS] About to execute: extract PeriodID from record")
        period_id = record.get('PeriodID')
        print(f"[ENRICH_RECORDS] PeriodID: {period_id}")

        print("[ENRICH_RECORDS] About to execute: check if period_id")
        if period_id:
            print(f"[ENRICH_RECORDS] About to execute: get_period_details for period_id={period_id}")
            period = get_period_details(period_id, logger)
            print(f"[ENRICH_RECORDS] Period details: {period}")

            print("[ENRICH_RECORDS] About to execute: add period details to enriched_record")
            enriched_record['PeriodNumber'] = period.get('PeriodNumber', '')
            enriched_record['PeriodYear'] = period.get('PeriodYear', '')
            enriched_record['WorkStartDate'] = period.get('WorkStartDate', '')
            enriched_record['WorkEndDate'] = period.get('WorkEndDate', '')
            print(f"[ENRICH_RECORDS] Period details added")

        print(f"[ENRICH_RECORDS] About to execute: append enriched_record to enriched list")
        enriched.append(enriched_record)
        print(f"[ENRICH_RECORDS] Enriched record appended, total: {len(enriched)}")

    print(f"[ENRICH_RECORDS] About to execute: logger.info 'Records enriched' with count={len(enriched)}")
    logger.info("Records enriched", count=len(enriched))
    print("[ENRICH_RECORDS] Info message logged")

    print(f"[ENRICH_RECORDS] Returning {len(enriched)} enriched records")
    return enriched


def get_contractor_details(contractor_id, logger):
    """
    Get contractor details from DynamoDB
    """
    print(f"[GET_CONTRACTOR] About to execute: get_contractor_details with contractor_id={contractor_id}")

    print(f"[GET_CONTRACTOR] About to execute: build PK and SK")
    pk = f'CONTRACTOR#{contractor_id}'
    sk = 'PROFILE'
    print(f"[GET_CONTRACTOR] PK: {pk}, SK: {sk}")

    print("[GET_CONTRACTOR] About to execute: dynamodb_client.table.get_item")
    response = dynamodb_client.table.get_item(
        Key={'PK': pk, 'SK': sk}
    )
    print(f"[GET_CONTRACTOR] get_item response: {response}")

    print("[GET_CONTRACTOR] About to execute: extract Item from response")
    item = response.get('Item', {})
    print(f"[GET_CONTRACTOR] Item: {item}")

    print("[GET_CONTRACTOR] Returning contractor details")
    return item


def get_umbrella_details(umbrella_id, logger):
    """
    Get umbrella company details from DynamoDB
    """
    print(f"[GET_UMBRELLA] About to execute: get_umbrella_details with umbrella_id={umbrella_id}")

    print(f"[GET_UMBRELLA] About to execute: build PK and SK")
    pk = f'UMBRELLA#{umbrella_id}'
    sk = 'PROFILE'
    print(f"[GET_UMBRELLA] PK: {pk}, SK: {sk}")

    print("[GET_UMBRELLA] About to execute: dynamodb_client.table.get_item")
    response = dynamodb_client.table.get_item(
        Key={'PK': pk, 'SK': sk}
    )
    print(f"[GET_UMBRELLA] get_item response: {response}")

    print("[GET_UMBRELLA] About to execute: extract Item from response")
    item = response.get('Item', {})
    print(f"[GET_UMBRELLA] Item: {item}")

    print("[GET_UMBRELLA] Returning umbrella details")
    return item


def get_period_details(period_id, logger):
    """
    Get pay period details from DynamoDB
    """
    print(f"[GET_PERIOD] About to execute: get_period_details with period_id={period_id}")

    print(f"[GET_PERIOD] About to execute: build PK and SK")
    pk = f'PERIOD#{period_id}'
    sk = 'PROFILE'
    print(f"[GET_PERIOD] PK: {pk}, SK: {sk}")

    print("[GET_PERIOD] About to execute: dynamodb_client.table.get_item")
    response = dynamodb_client.table.get_item(
        Key={'PK': pk, 'SK': sk}
    )
    print(f"[GET_PERIOD] get_item response: {response}")

    print("[GET_PERIOD] About to execute: extract Item from response")
    item = response.get('Item', {})
    print(f"[GET_PERIOD] Item: {item}")

    print("[GET_PERIOD] Returning period details")
    return item


def calculate_statistics(records, logger):
    """
    Calculate totals, averages, and statistics from pay records
    """
    print(f"[CALC_STATS] About to execute: calculate_statistics with {len(records)} records")
    print(f"[CALC_STATS] About to execute: logger.info 'Calculating statistics'")
    logger.info("Calculating statistics", count=len(records))
    print("[CALC_STATS] Info message logged")

    print("[CALC_STATS] About to execute: check if not records")
    if not records:
        print("[CALC_STATS] No records, returning empty stats")
        return {
            'total_amount': 0,
            'total_vat': 0,
            'total_gross': 0,
            'total_days': 0,
            'total_hours': 0,
            'average_day_rate': 0,
            'record_count': 0
        }

    print("[CALC_STATS] About to execute: initialize accumulators")
    total_amount = Decimal('0')
    total_vat = Decimal('0')
    total_gross = Decimal('0')
    total_days = Decimal('0')
    total_hours = Decimal('0')
    day_rates = []
    print(f"[CALC_STATS] Accumulators initialized")

    print(f"[CALC_STATS] About to execute: iterate through {len(records)} records")
    for idx, record in enumerate(records):
        print(f"[CALC_STATS] About to execute: process record {idx+1}/{len(records)}")

        print(f"[CALC_STATS] About to execute: extract Amount from record")
        amount = record.get('Amount', Decimal('0'))
        print(f"[CALC_STATS] Amount: {amount}")

        print(f"[CALC_STATS] About to execute: add amount to total_amount")
        total_amount += amount
        print(f"[CALC_STATS] total_amount: {total_amount}")

        print(f"[CALC_STATS] About to execute: extract VATAmount from record")
        vat = record.get('VATAmount', Decimal('0'))
        print(f"[CALC_STATS] VATAmount: {vat}")

        print(f"[CALC_STATS] About to execute: add vat to total_vat")
        total_vat += vat
        print(f"[CALC_STATS] total_vat: {total_vat}")

        print(f"[CALC_STATS] About to execute: extract GrossAmount from record")
        gross = record.get('GrossAmount', Decimal('0'))
        print(f"[CALC_STATS] GrossAmount: {gross}")

        print(f"[CALC_STATS] About to execute: add gross to total_gross")
        total_gross += gross
        print(f"[CALC_STATS] total_gross: {total_gross}")

        print(f"[CALC_STATS] About to execute: extract UnitDays from record")
        days = record.get('UnitDays', Decimal('0'))
        print(f"[CALC_STATS] UnitDays: {days}")

        print(f"[CALC_STATS] About to execute: add days to total_days")
        total_days += days
        print(f"[CALC_STATS] total_days: {total_days}")

        print(f"[CALC_STATS] About to execute: extract TotalHours from record")
        hours = record.get('TotalHours', Decimal('0'))
        print(f"[CALC_STATS] TotalHours: {hours}")

        print(f"[CALC_STATS] About to execute: add hours to total_hours")
        total_hours += hours
        print(f"[CALC_STATS] total_hours: {total_hours}")

        print(f"[CALC_STATS] About to execute: extract DayRate from record")
        day_rate = record.get('DayRate')
        print(f"[CALC_STATS] DayRate: {day_rate}")

        print("[CALC_STATS] About to execute: check if day_rate")
        if day_rate:
            print(f"[CALC_STATS] About to execute: append day_rate to day_rates list")
            day_rates.append(day_rate)
            print(f"[CALC_STATS] day_rates count: {len(day_rates)}")

    print("[CALC_STATS] About to execute: calculate average_day_rate")
    average_day_rate = sum(day_rates) / len(day_rates) if day_rates else Decimal('0')
    print(f"[CALC_STATS] average_day_rate: {average_day_rate}")

    print("[CALC_STATS] About to execute: build stats dict")
    stats = {
        'total_amount': float(total_amount),
        'total_vat': float(total_vat),
        'total_gross': float(total_gross),
        'total_days': float(total_days),
        'total_hours': float(total_hours),
        'average_day_rate': float(average_day_rate),
        'record_count': len(records)
    }
    print(f"[CALC_STATS] stats: {stats}")

    print(f"[CALC_STATS] About to execute: logger.info 'Statistics calculated'")
    logger.info("Statistics calculated", stats=stats)
    print("[CALC_STATS] Info message logged")

    print("[CALC_STATS] Returning stats")
    return stats


def calculate_umbrella_breakdown(records, logger):
    """
    Calculate breakdown by umbrella company
    """
    print(f"[UMBRELLA_BREAKDOWN] About to execute: calculate_umbrella_breakdown with {len(records)} records")
    print(f"[UMBRELLA_BREAKDOWN] About to execute: logger.info 'Calculating umbrella breakdown'")
    logger.info("Calculating umbrella breakdown", count=len(records))
    print("[UMBRELLA_BREAKDOWN] Info message logged")

    print("[UMBRELLA_BREAKDOWN] About to execute: initialize breakdown = {}")
    breakdown = {}
    print(f"[UMBRELLA_BREAKDOWN] breakdown initialized: {breakdown}")

    print(f"[UMBRELLA_BREAKDOWN] About to execute: iterate through {len(records)} records")
    for idx, record in enumerate(records):
        print(f"[UMBRELLA_BREAKDOWN] About to execute: process record {idx+1}/{len(records)}")

        print(f"[UMBRELLA_BREAKDOWN] About to execute: extract UmbrellaID from record")
        umbrella_id = record.get('UmbrellaID')
        print(f"[UMBRELLA_BREAKDOWN] UmbrellaID: {umbrella_id}")

        print("[UMBRELLA_BREAKDOWN] About to execute: check if not umbrella_id")
        if not umbrella_id:
            print("[UMBRELLA_BREAKDOWN] No umbrella_id, skipping")
            continue

        print("[UMBRELLA_BREAKDOWN] About to execute: check if umbrella_id not in breakdown")
        if umbrella_id not in breakdown:
            print(f"[UMBRELLA_BREAKDOWN] About to execute: get_umbrella_details for umbrella_id={umbrella_id}")
            umbrella = get_umbrella_details(umbrella_id, logger)
            print(f"[UMBRELLA_BREAKDOWN] Umbrella details: {umbrella}")

            print(f"[UMBRELLA_BREAKDOWN] About to execute: initialize breakdown entry for umbrella_id")
            breakdown[umbrella_id] = {
                'umbrella_name': umbrella.get('LegalName', ''),
                'umbrella_code': umbrella.get('ShortCode', ''),
                'total_amount': Decimal('0'),
                'total_vat': Decimal('0'),
                'total_gross': Decimal('0'),
                'total_days': Decimal('0'),
                'record_count': 0
            }
            print(f"[UMBRELLA_BREAKDOWN] Breakdown entry initialized for umbrella_id")

        print(f"[UMBRELLA_BREAKDOWN] About to execute: update breakdown for umbrella_id")
        breakdown[umbrella_id]['total_amount'] += record.get('Amount', Decimal('0'))
        breakdown[umbrella_id]['total_vat'] += record.get('VATAmount', Decimal('0'))
        breakdown[umbrella_id]['total_gross'] += record.get('GrossAmount', Decimal('0'))
        breakdown[umbrella_id]['total_days'] += record.get('UnitDays', Decimal('0'))
        breakdown[umbrella_id]['record_count'] += 1
        print(f"[UMBRELLA_BREAKDOWN] Breakdown updated for umbrella_id")

    print("[UMBRELLA_BREAKDOWN] About to execute: convert Decimal to float in breakdown")
    for umbrella_id in breakdown:
        print(f"[UMBRELLA_BREAKDOWN] About to execute: convert values for umbrella_id={umbrella_id}")
        breakdown[umbrella_id]['total_amount'] = float(breakdown[umbrella_id]['total_amount'])
        breakdown[umbrella_id]['total_vat'] = float(breakdown[umbrella_id]['total_vat'])
        breakdown[umbrella_id]['total_gross'] = float(breakdown[umbrella_id]['total_gross'])
        breakdown[umbrella_id]['total_days'] = float(breakdown[umbrella_id]['total_days'])
        print(f"[UMBRELLA_BREAKDOWN] Values converted for umbrella_id={umbrella_id}")

    print(f"[UMBRELLA_BREAKDOWN] About to execute: logger.info 'Umbrella breakdown calculated'")
    logger.info("Umbrella breakdown calculated", breakdown_count=len(breakdown))
    print("[UMBRELLA_BREAKDOWN] Info message logged")

    print(f"[UMBRELLA_BREAKDOWN] Returning breakdown with {len(breakdown)} umbrellas")
    return breakdown


def generate_csv(records, report_type='summary', logger=None):
    """
    Generate CSV file from records
    """
    print(f"[GENERATE_CSV] About to execute: generate_csv with {len(records)} records, report_type={report_type}")
    print(f"[GENERATE_CSV] About to execute: logger.info 'Generating CSV'")
    logger.info("Generating CSV", count=len(records), report_type=report_type)
    print("[GENERATE_CSV] Info message logged")

    print("[GENERATE_CSV] About to execute: create StringIO buffer")
    output = io.StringIO()
    print(f"[GENERATE_CSV] StringIO buffer created: {output}")

    print("[GENERATE_CSV] About to execute: create csv.writer")
    writer = csv.writer(output)
    print(f"[GENERATE_CSV] csv.writer created: {writer}")

    print("[GENERATE_CSV] About to execute: check if records")
    if not records:
        print("[GENERATE_CSV] No records, writing empty CSV header")
        writer.writerow(['No records found'])
        print("[GENERATE_CSV] Empty header written")
        print("[GENERATE_CSV] About to execute: get CSV value from buffer")
        csv_data = output.getvalue()
        print(f"[GENERATE_CSV] CSV data: {len(csv_data)} bytes")
        print("[GENERATE_CSV] Returning CSV data")
        return csv_data

    print(f"[GENERATE_CSV] About to execute: determine CSV headers for report_type={report_type}")
    if report_type == 'summary':
        print("[GENERATE_CSV] About to execute: set headers for summary report")
        headers = [
            'RecordID', 'ContractorID', 'UmbrellaID', 'PeriodID',
            'EmployeeID', 'UnitDays', 'DayRate', 'Amount', 'VATAmount', 'GrossAmount',
            'TotalHours', 'RecordType', 'CreatedAt'
        ]
        print(f"[GENERATE_CSV] Headers: {headers}")
    else:
        print("[GENERATE_CSV] About to execute: set headers for detailed report")
        headers = [
            'RecordID', 'ContractorName', 'ContractorJobTitle', 'UmbrellaName', 'UmbrellaCode',
            'PeriodNumber', 'PeriodYear', 'WorkStartDate', 'WorkEndDate',
            'EmployeeID', 'UnitDays', 'DayRate', 'Amount', 'VATAmount', 'GrossAmount',
            'TotalHours', 'RecordType', 'Notes', 'CreatedAt'
        ]
        print(f"[GENERATE_CSV] Headers: {headers}")

    print("[GENERATE_CSV] About to execute: write header row")
    writer.writerow(headers)
    print("[GENERATE_CSV] Header row written")

    print(f"[GENERATE_CSV] About to execute: iterate through {len(records)} records")
    for idx, record in enumerate(records):
        print(f"[GENERATE_CSV] About to execute: process record {idx+1}/{len(records)}")

        print("[GENERATE_CSV] About to execute: build row from record")
        if report_type == 'summary':
            print("[GENERATE_CSV] About to execute: build summary row")
            row = [
                record.get('RecordID', ''),
                record.get('ContractorID', ''),
                record.get('UmbrellaID', ''),
                record.get('PeriodID', ''),
                record.get('EmployeeID', ''),
                str(record.get('UnitDays', '')),
                str(record.get('DayRate', '')),
                str(record.get('Amount', '')),
                str(record.get('VATAmount', '')),
                str(record.get('GrossAmount', '')),
                str(record.get('TotalHours', '')),
                record.get('RecordType', ''),
                record.get('CreatedAt', '')
            ]
            print(f"[GENERATE_CSV] Summary row built")
        else:
            print("[GENERATE_CSV] About to execute: build detailed row")
            row = [
                record.get('RecordID', ''),
                record.get('ContractorName', ''),
                record.get('ContractorJobTitle', ''),
                record.get('UmbrellaName', ''),
                record.get('UmbrellaCode', ''),
                str(record.get('PeriodNumber', '')),
                str(record.get('PeriodYear', '')),
                record.get('WorkStartDate', ''),
                record.get('WorkEndDate', ''),
                record.get('EmployeeID', ''),
                str(record.get('UnitDays', '')),
                str(record.get('DayRate', '')),
                str(record.get('Amount', '')),
                str(record.get('VATAmount', '')),
                str(record.get('GrossAmount', '')),
                str(record.get('TotalHours', '')),
                record.get('RecordType', ''),
                record.get('Notes', ''),
                record.get('CreatedAt', '')
            ]
            print(f"[GENERATE_CSV] Detailed row built")

        print(f"[GENERATE_CSV] About to execute: write row to CSV")
        writer.writerow(row)
        print(f"[GENERATE_CSV] Row {idx+1} written")

    print("[GENERATE_CSV] About to execute: get CSV value from buffer")
    csv_data = output.getvalue()
    print(f"[GENERATE_CSV] CSV data: {len(csv_data)} bytes")

    print(f"[GENERATE_CSV] About to execute: logger.info 'CSV generated' with size={len(csv_data)}")
    logger.info("CSV generated", size=len(csv_data), rows=len(records))
    print("[GENERATE_CSV] Info message logged")

    print("[GENERATE_CSV] Returning CSV data")
    return csv_data


def upload_to_s3(csv_data, report_type, filters, logger):
    """
    Upload CSV to S3 and return key
    """
    print(f"[UPLOAD_S3] About to execute: upload_to_s3 with csv_data size={len(csv_data)}, report_type={report_type}")
    print(f"[UPLOAD_S3] About to execute: logger.info 'Uploading to S3'")
    logger.info("Uploading to S3", report_type=report_type, filters=filters)
    print("[UPLOAD_S3] Info message logged")

    print("[UPLOAD_S3] About to execute: generate timestamp")
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    print(f"[UPLOAD_S3] timestamp: {timestamp}")

    print("[UPLOAD_S3] About to execute: generate report_id")
    report_id = str(uuid.uuid4())[:8]
    print(f"[UPLOAD_S3] report_id: {report_id}")

    print("[UPLOAD_S3] About to execute: build s3_key")
    s3_key = f"reports/{report_type}/{timestamp}_{report_id}.csv"
    print(f"[UPLOAD_S3] s3_key: {s3_key}")

    print("[UPLOAD_S3] About to execute: check if not s3_bucket")
    if not s3_bucket:
        print("[UPLOAD_S3] About to execute: raise ValueError for missing S3_BUCKET_NAME")
        raise ValueError("S3_BUCKET_NAME environment variable not set")

    print(f"[UPLOAD_S3] About to execute: s3_client.put_object to bucket={s3_bucket}, key={s3_key}")
    s3_client.put_object(
        Bucket=s3_bucket,
        Key=s3_key,
        Body=csv_data.encode('utf-8'),
        ContentType='text/csv',
        Metadata={
            'report_type': report_type,
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'filters': json.dumps(filters)
        }
    )
    print(f"[UPLOAD_S3] S3 upload complete: s3://{s3_bucket}/{s3_key}")

    print(f"[UPLOAD_S3] About to execute: logger.info 'Uploaded to S3' with s3_key={s3_key}")
    logger.info("Uploaded to S3", bucket=s3_bucket, key=s3_key)
    print("[UPLOAD_S3] Info message logged")

    print(f"[UPLOAD_S3] Returning s3_key: {s3_key}")
    return s3_key
