import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('t_archivos_UTEC')

def lambda_handler(event, context):
    resultados = []

    for record in event['Records']:
        archivo_json = json.loads(record['Sns']['Message'])
        datos = archivo_json['archivo_datos']

        archivo = {
            'tenant_id': archivo_json['tenant_id'],
            'archivo_id': archivo_json['archivo_id'],
            'archivo_datos': datos,
            'codigo_curso': datos['codigo_curso'],
            'codigo_alumno': datos['codigo_alumno']
        }

        print('Ítem a guardar:', json.dumps(archivo))
        table.put_item(Item=archivo)
        resultados.append(archivo['archivo_id'])

    return {
        'statusCode': 200,
        'archivos_guardados': resultados
    }
