# ====================================================================================================
# Auteur: Romain Castagné
# Société: CGI
# Date de génération: 28 juin 2024
# Version: v1.2
#
# Description:
# Ce script traite des fichiers JSON provenant du système MES (Manufacturing Execution System) pour 
# extraire des informations spécifiques et les enregistrer dans des fichiers CSV. Le script gère plusieurs 
# opérations, telles que le chargement des fichiers JSON, l'extraction des informations pertinentes
# et la sauvegarde des fichiers de sortie dans des dossiers spécifiques. Les fichiers CSV générés 
# sont destinés à être intégrés dans le système PI (Plant Information) via un connecteur PI UFL.
#
# Format du fichier CSV:
# Chaque ligne du fichier CSV est structurée comme suit:
# [Valeur, Timestamp, TagName]
#
# Paramètres:
# - --input_json_folder: Chemin vers les fichiers JSON d'entrée. Par défaut: 'Input\\Nersac'
# - --output_folder: Dossier des fichiers d'entrée UFL. Par défaut: 'UFL_Input'
# - --backup_folder: Dossier de sauvegarde des fichiers originaux. Par défaut: 'Done'
# - --log_folder: Dossier des journaux du script. Par défaut: 'Logs'
# - --suffixe: Suffixe du tag. Par défaut: '.PV'
#
# ====================================================================================================

import datetime
import json
import argparse
import csv
import codecs
import os
import time
import logging
import re
import sys

# Ajouter le chemin du dossier racine du projet à sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))
import _lib.progressbar as progressbar

def load_json(json_file):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading JSON file {json_file}: {e}")
        return None

def get_wo_dates(data, date_type):
    if date_type not in ['StartDate', 'EndDate']:
        raise ValueError("Le type de date doit être 'StartDate' ou 'EndDate'.")
    
    if data and data[0].get('DataHeader'):
        if date_type == 'StartDate':
            return data[0]['DataHeader'][0]['Properties'][0]['Value']
        elif date_type == 'EndDate':
            return data[0]['DataHeader'][-1]['Properties'][1]['Value']
    
    return None

def convert_datetime_format(datetime_str):
    return datetime_str.replace('T', ' ')

def write_csv_output_file(all_data, file_name, output_folder):
    file_path = os.path.join(output_folder, f'{file_name}.csv')
    try:
        with codecs.open(file_path, 'w', encoding='utf-8') as f:
            writer = csv.writer(f)
            for row in all_data:
                writer.writerow(row)
        logging.info(f"CSV file written: {file_path}")
    except Exception as e:
        logging.error(f"Error writing CSV file {file_path}: {e}")

def create_folders_if_not_exist(folders):
    for folder in folders:
        folder_path = os.path.join(os.path.dirname(__file__), folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

def extract_work_center_info(work_center_name):
    match = re.match(r'(\d{3})\w{5}_(\w{2})(\w)\w{5}_(\w{4})(\d{2})', work_center_name)
    if match:
        prefixe_affiliate = 'ACCBBD_V1' if match.group(1) == '130' else 'ACCNR_NEW04'
        return {
            'site_code': prefixe_affiliate,
            'process_type': match.group(2),
            'polarity': match.group(3),
            'equipment': match.group(4),
            'equipment_code': match.group(5)
        }
    return None

def process_file(file_path, output_folder, backup_folder, args):
    logging.info(f'Processing file {file_path}')
    data = load_json(file_path)
    if not data:
        return
    
    work_center_name = data[0].get('WorkCenterName', '')
    work_center_info = extract_work_center_info(work_center_name)
    
    if work_center_info:
        logging.info(f"--- Site Code: {work_center_info['site_code']}")
        logging.info(f"--- Process Type: {work_center_info['process_type']}")
        logging.info(f"--- Polarity: {work_center_info['polarity']}")
        logging.info(f"--- Equipment: {work_center_info['equipment']}")
        logging.info(f"--- Equipment Code: {work_center_info['equipment_code']}")

        all_data = []
        work_order_start_date = get_wo_dates(data, "StartDate")
        prefixe_tag_name = f"{work_center_info['site_code']}_MES_{work_center_info['process_type']}{work_center_info['polarity']}_{work_center_info['equipment']}{work_center_info['equipment_code']}_"
        reference_value = data[0]['Reference']
        reference_tag_name = f"{prefixe_tag_name}REFERENCE{args.suffixe}"
        all_data.append([reference_value, convert_datetime_format(work_order_start_date), reference_tag_name])

        numjob = 0
        for job in data[0]['DataHeader']:
            numjob += 1
            job_name = f'JOB{numjob}_'
            job_timestamp = convert_datetime_format(job['Properties'][0]['Value'])
            job_id_value = job['JobID']
            job_id_tag_name = f"{prefixe_tag_name}{job_name}ID{args.suffixe}"
            # segment_name_value = job['SegmentName']
            # segment_name_tag_name = f"{prefixe_tag_name}{job_name}SEGMENTNAME{args.suffixe}"

            all_data.append([job_id_value, job_timestamp, job_id_tag_name])
            # all_data.append([segment_name_value, job_timestamp, segment_name_tag_name])   # SEGMENTNAME constant : attribut statique.

            for property in job['Properties']:
                property_name = property['PropertyID']
                property_tag_name = f"{prefixe_tag_name}{job_name}{property_name}{args.suffixe}"
                property_value = property['Value']
                if property_name == 'DUREEPROD':
                    pass
                elif property_name in ['STARTDATE', 'ENDDATE']:
                    property_tag_name = f"{prefixe_tag_name}{job_name}STATUS{args.suffixe}"
                    property_timestamp = convert_datetime_format(property_value)
                    property_value = 'START' if property_name == 'STARTDATE' else 'STOP'
                    all_data.append([property_value, property_timestamp, property_tag_name])
                else:
                    all_data.append([property_value, job_timestamp, property_tag_name])
            #for data in job['Data']

        file_name = f'MES_to_UFL_{work_center_info["process_type"]}{work_center_info["polarity"]}_{work_center_info["equipment"]}{work_center_info["equipment_code"]}_{datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S-%f")[:-3]}'
        write_csv_output_file(all_data, file_name, output_folder)
        os.rename(file_path, os.path.join(backup_folder, os.path.basename(file_path)))
        time.sleep(0.1)
    else:
        logging.warning("No match found for work center name pattern.")

def generate_PI_tags_list(output_folder, log_folder):
    inputPath = output_folder
    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    outputfile = os.path.join(os.path.dirname(__file__), log_folder, f'tagsList_{timestamp}.txt')

    unique_tags = set()

    input_files = [f for f in os.listdir(inputPath) if os.path.isfile(os.path.join(inputPath, f))]
    
    # Lire tous les fichiers d'entrée et collecter les tags uniques
    for input_file in input_files:
        with open(os.path.join(inputPath, input_file), 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                parts = line.split(',')
                if len(parts) > 2:
                    tagName = ','.join(parts[2:]).strip()
                    unique_tags.add(tagName)

    # Trier les tags uniques par ordre alphabétique
    sorted_unique_tags = sorted(unique_tags)

    # Écrire les tags uniques triés dans le fichier de sortie
    with open(outputfile, 'w', encoding='utf-8') as f:
        for tag in sorted_unique_tags:
            f.write(tag + '\n')

    logging.info(f"Tags list written to: {outputfile}")

def main(input_json_folder, output_folder, backup_folder, log_folder, suffixe):
    os.system('clear')
    create_folders_if_not_exist([input_json_folder, output_folder, backup_folder, log_folder])
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=os.path.join(os.path.dirname(__file__), log_folder, 'SplitMESFiles_logs_' + datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S") + '.log'))
    logging.info(f"## Starting script {os.path.basename(__file__)} ##")
    logging.info(f"--- Input JSON Folder: {input_json_folder}")
    logging.info(f"--- Output folder: {output_folder}")
    logging.info(f"--- backup folder: {backup_folder}")
    logging.info(f"--- log folder: {log_folder}")
    logging.info(f"--- Suffix: {suffixe}")
    
    files = [f for f in os.listdir(input_json_folder) if os.path.isfile(os.path.join(input_json_folder, f))]
    for i, f in enumerate(files, 1):
        progressbar.print_progress_bar(i, len(files), f'Processing file {f}')
        process_file(os.path.join(input_json_folder, f), output_folder, backup_folder, args)
    generate_PI_tags_list(output_folder, log_folder)
    logging.info(f"## Ending script {os.path.basename(__file__)} ##")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some parameters.")
    parser.add_argument('--input_json_folder', type=str, default='Input\\Nersac', help='Path to the JSON input files. Default: %(default)s')
    parser.add_argument('--output_folder', type=str, default='UFL_Input', help='UFL input files folder. Default: %(default)s')
    parser.add_argument('--backup_folder', type=str, default='Done', help='Copy of original file folder. Default: %(default)s')
    parser.add_argument('--log_folder', type=str, default='Logs', help='Logs folder of the script. Default: %(default)s')
    parser.add_argument('--suffixe', type=str, default='.PV', help='Suffixe of the tag. Default: %(default)s')
    args = parser.parse_args()

    os.chdir(os.path.dirname(__file__))
    main(args.input_json_folder, 
         args.output_folder,
         args.backup_folder,
         args.log_folder,
         args.suffixe)
