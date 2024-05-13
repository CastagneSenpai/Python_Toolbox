import json
import csv
import codecs

def load_Json(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

# Paramètre date_type doit être 'StartDate' ou 'EndDate'
def get_WO_Dates(data, date_type):
    date_value = None

    # Vérifier si le type de date est valide
    if date_type not in ['StartDate', 'EndDate']:
        raise ValueError("Le type de date doit être 'StartDate' ou 'EndDate'.")

    # Compter le nombre de jobs
    num_jobs = len(data[0]['DataHeader'])

    # Si au moins un job existe
    if num_jobs > 0:
        if date_type == 'StartDate':
            # Accéder au premier job pour obtenir la StartDate
            date_value = data[0]['DataHeader'][0]['Properties'][0]['Value']
        elif date_type == 'EndDate':
            # Accéder au dernier job pour obtenir la EndDate
            date_value = data[0]['DataHeader'][-1]['Properties'][1]['Value']

    return date_value

def write_CSV_OutputFile(all_data):
    with codecs.open('output_data.csv', 'w', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['TagName', 'Value', 'Timestamp'])  # Écrire l'en-tête

        # Écrire chaque ligne de données
        for row in all_data:
            writer.writerow(row)


def main(json_file, prefixe_tagName, suffixe_tagName):
    # Chargement du fichier input du MES (format Json)
    data = load_Json(json_file)

    # Initialiser une liste pour stocker toutes les données
    all_data = []

    # Informations du Work Order (WO)
    WorkOrder_StartDate = get_WO_Dates(data, "StartDate")
    
    Reference_Value = data[0]['Reference']
    Reference_TagName = prefixe_tagName + 'Reference' + suffixe_tagName

    all_data.append([Reference_TagName, Reference_Value, WorkOrder_StartDate])

    # Informations des jobs
    for job in data[0]['DataHeader']:
        job_TimeStamp = job['Properties'][0]['Value']
        jobID_Value = job['JobID']
        JobID_TagName = prefixe_tagName + 'JobID' + suffixe_tagName
        segmentName_Value = job['SegmentName']
        segmentName_TagName = prefixe_tagName + 'SegmentName' + suffixe_tagName

        all_data.append([JobID_TagName, jobID_Value, job_TimeStamp])
        all_data.append([segmentName_TagName, segmentName_Value, job_TimeStamp])

        # Informations des propriétés des jobs
        for property in job['Properties']:
            property_Name = property['PropertyID'] #Ex: STARTDATE, ENDDATE, NUMOFDAY, TYPEOFPROD, DUREEPROD
            property_TagName = prefixe_tagName + property_Name + suffixe_tagName
            property_Value = property['Value']

            all_data.append([property_TagName, property_Value, job_TimeStamp])

    write_CSV_OutputFile(all_data)
    input("Fin de la fonction principale, appuyer sur une touche pour fermer.")
    
# Call the main method properly
if __name__ == "__main__":
    main('JSON_Tracabilite.json', 'ACCBBD_V1_MES_MIA_Ligne1_', '.PV')