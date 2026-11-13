import json
import boto3
from urllib.parse import unquote_plus

s3 = boto3.client('s3')
sns = boto3.client('sns')

TOPIC_ARN = 'arn:aws:sns:us-east-1:197608976686:TemaNuevoArchivo'

def lambda_handler(event, context):
    resultados = []

    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']

        # La clave del evento de S3 llega codificada como URL.
        archivo_id = unquote_plus(record['s3']['object']['key'])
        partes = archivo_id.split('/')

        if len(partes) < 3 or partes[0] != 'universidades':
            raise ValueError(f'Ruta inesperada: {archivo_id}')

        tenant_id = partes[1]  # universidades/UTEC/archivo03.txt → UTEC

        # Recupera los metadatos personalizados sin descargar el archivo.
        respuesta_s3 = s3.head_object(
            Bucket=bucket_name,
            Key=archivo_id
        )
        metadata = respuesta_s3['Metadata']

        codigo_curso = metadata.get('codigo-curso')
        codigo_alumno = metadata.get('codigo-alumno')

        if not codigo_curso or not codigo_alumno:
            raise ValueError(
                f'Falta codigo-curso o codigo-alumno en los '
                f'metadatos de s3://{bucket_name}/{archivo_id}'
            )

        archivo = {
            'tenant_id': tenant_id,
            'archivo_id': archivo_id,
            'archivo_datos': {
                'last_modified': record['eventTime'],
                'size': record['s3']['object']['size'],
                'bucket_name': bucket_name,
                'codigo_curso': codigo_curso,
                'codigo_alumno': codigo_alumno
            }
        }

        print('Archivo procesado:', json.dumps(archivo))

        respuesta_sns = sns.publish(
            TopicArn=TOPIC_ARN,
            Subject='Nuevo Archivo',
            Message=json.dumps(archivo),
            MessageAttributes={
                'tenant_id': {
                    'DataType': 'String',
                    'StringValue': tenant_id
                }
            }
        )
        resultados.append(respuesta_sns['MessageId'])

    return {
        'statusCode': 200,
        'message_ids': resultados
    }
