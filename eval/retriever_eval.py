import psycopg2 
import eval
import random
import sys
import argparse
import os
import traceback

folder_a_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'rag'))  

# Add the folder path to sys.path  
sys.path.insert(0, folder_a_path)  

import app as rag_app

db_user = 'postgres'
db_password = 'CS230password'
db_host = 'database-1.cdi4gywsaigf.us-east-2.rds.amazonaws.com'
db_port = 5432
db_name = 'postgres'

db_connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# DB schema
#   Column   |          Type          | Collation | Nullable | Default 
# -----------+------------------------+-----------+----------+---------
#  id        | integer                |           |          | 
#  text      | text                   |           |          | 
#  source    | character varying(255) |           |          | 
#  embedding | vector(384)            |           |          |        

def add_questions_column(conn=None, table_name='your_table_name'):
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                               WHERE table_name='{table_name}' AND column_name='questions') THEN
                    ALTER TABLE {table_name} ADD COLUMN "questions" TEXT[];
                END IF;
            END
            $$;
        """)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()

def add_topk_rank_column(conn=None, table_name='your_table_name'):
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                               WHERE table_name='{table_name}' AND column_name='topk_rank') THEN
                    ALTER TABLE {table_name} ADD COLUMN "topk_rank" INT[];
                END IF;
            END
            $$;
        """)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()


def get_row_count(conn=None, table_name='your_table_name'):
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        return row_count
    except Exception as e:
        raise e
    finally:
        cursor.close()

def get_max_id(conn=None, table_name='your_table_name'):
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SELECT MAX(id) FROM {table_name}")
        max_id = cursor.fetchone()[0]
        return max_id
    except Exception as e:
        raise e
    finally:
        cursor.close()

def insert_questions(conn, table_name: str, row_id: int, questions: list[str]):
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"""
            UPDATE {table_name}
            SET questions = %s
            WHERE id = %s
        """, (questions, row_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()

def get_questions_by_id(conn, table_name: str, row_id: int) -> list[str]:
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT questions FROM {table_name} WHERE id = %s", (row_id,))
        questions = cursor.fetchone()
        if questions:
            return questions[0]
        else:
            raise ValueError(f"Row with id {row_id} not found")
    except Exception as e:
        raise e
    finally:
        cursor.close()


def insert_topk_rank(conn, table_name: str, row_id: int, topk_rank: list[int]):
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"""
            UPDATE {table_name}
            SET topk_rank = %s
            WHERE id = %s
        """, (topk_rank, row_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()

def read_text_by_id(conn, table_name: str, row_id: int):
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SELECT text FROM {table_name} WHERE id = %s", (row_id,))
        text = cursor.fetchone()
        if text:
            return text[0]
        else:
            raise ValueError(f"Row with id {row_id} not found")
    except Exception as e:
        raise e
    finally:
        cursor.close()

def process_and_insert_questions(conn, model_name="your_model_name", table_name='your_table_name', debug=False,  idList=[]):
    max_id = get_max_id(conn, table_name)
    questionClient=eval.GenerateQuestionsBasedOnText(model_name)
    start = 1

    rangeList = range(start, max_id+1)
    if len(idList) > 0:
        rangeList = idList

    for row_id in (random.sample(rangeList, 5) if debug else rangeList):
        try:
            text = read_text_by_id(conn, table_name, row_id)
            questions = questionClient.generate_questions(text)
            if debug:
                print(f"Processing row {row_id}\nQuestions: {questions}\nText: {text}")
                if row_id == rangeList[-1]:
                    return
            else:
                if row_id % 50 == 1:
                    print(f"Questions: {questions}\nText: {text}\n")
                insert_questions(conn, table_name, row_id, questions)
        except Exception as e:
            print(f"Error processing row {row_id}: {e}")
            continue

def add_topk_rank_result(conn, table_name='your_table_name', debug=False,  idList=[]):
    max_id = get_max_id(conn, table_name)
    rangeList = range(1, max_id+1)
    if len(idList) > 0:
        rangeList = idList
    
    for row_id in (random.sample(rangeList, 5) if debug else rangeList):
        try:
            questions = get_questions_by_id(conn, table_name, row_id)
            result = []
            for question in questions:
                topk_rank_result = rag_app.get_documents(table_name, question, 20)              
                topk_doc_id = [doc.id for doc in topk_rank_result]
                doc_index = next((index for index, doc in enumerate(topk_rank_result) if doc.id == row_id), -1)
                result.append(doc_index)
                if debug:
                    print(f"Topk doc id: {topk_doc_id}\n, result: {result}")
                
            if debug:
                print(f"Processing row {row_id}\n, result: {result}")
                if row_id == rangeList[-1]:
                    return
            else:
                if row_id % 50 == 1:
                    print(f"Topk doc id: {topk_doc_id}\n, result: {result}")
                insert_topk_rank(conn, table_name, row_id, result)
        except Exception as e:
            print(f"Error processing row {row_id}: {e}")
            traceback.print_exc()
            if debug:
                return
            continue
    


    
def count_and_get_empty_questions(conn, table_name='your_table_name', limit=100):
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SELECT id FROM {table_name} WHERE questions IS NULL OR array_length(questions, 1) = 0 ORDER BY RANDOM() LIMIT {limit}")
        empty_rows = cursor.fetchall()

        cursor.execute(f"SELECT count(*) FROM {table_name} WHERE questions IS NULL OR array_length(questions, 1) = 0 ") 
        empty_count = cursor.fetchone()[0]   

        empty_ids = [row[0] for row in empty_rows]
        return empty_count, empty_ids
    except Exception as e:
        raise e
    finally:
        cursor.close()

def count_and_get_empty_topk_rank(conn, table_name='your_table_name', limit=100):
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SELECT id FROM {table_name} WHERE (topk_rank IS NULL OR array_length(topk_rank, 1) = 0) AND questions IS NOT NULL AND array_length(questions, 1) > 0 ORDER BY RANDOM() limit {limit}")
        empty_rows = cursor.fetchall()

        cursor.execute(f"SELECT count(*) FROM {table_name} WHERE (topk_rank IS NULL OR array_length(topk_rank, 1) = 0) AND questions IS NOT NULL AND array_length(questions, 1) > 0") 
        empty_count = cursor.fetchone()[0]   

        empty_ids = [row[0] for row in empty_rows]
        return empty_count, empty_ids
    except Exception as e:
        raise e
    finally:
        cursor.close()

def calculate_average_hit_rate(conn=None, table_name='your_table_name', topk=5):
    if conn is None:
        conn = psycopg2.connect(db_connection_string)

    cursor = conn.cursor()
    
    try:
        cursor.execute(f"""
            SELECT 
                SUM(CASE WHEN rank BETWEEN 0 AND {topk} THEN 1 ELSE 0 END)::float / COUNT(*)
            FROM (
                SELECT unnest(topk_rank) AS rank
                FROM {table_name}
                WHERE topk_rank IS NOT NULL AND array_length(topk_rank, 1) > 0
            ) AS ranks
        """)
        average_hit_rate = cursor.fetchone()[0]
        return average_hit_rate if average_hit_rate is not None else 0.0
    except Exception as e:
        raise e
    finally:
        cursor.close()

def getConnection():
    conn = psycopg2.connect(db_connection_string)
    return conn

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process table name.')
    parser.add_argument('table_name', type=str, choices=['document_semantic_split', 'document_recursive_split_rst_separator_1000_50', 'document_recursive_split_default_300_50'], help='The name of the table to process')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--fillquestions', action='store_true', help='Fill missing questions')
    parser.add_argument('--filltopkranks', action='store_true', help='Fill missing topk ranks')
    parser.add_argument('--hitrate', action='store_true', help='The hit rate threshold')
 
    
    # Example usage:
    # python retriever_eval.py your_table_name --debug --progress 0.5
    args = parser.parse_args()
    
    # Print all parsed values
    print(f"Table Name: {args.table_name}")
    print(f"Debug Mode: {args.debug}")

    conn = psycopg2.connect(db_connection_string)
    
    table_name = args.table_name
    debug = args.debug
    fill_questions = args.fillquestions
    fill_topk_ranks = args.filltopkranks
    hit_rate = args.hitrate

    if hit_rate:
        ks = [1,3,5,10,20]
        for k in ks:
            print(f"Average hit rate for top-{k}: {calculate_average_hit_rate(conn, table_name, k)}")
        sys.exit(0)

    if fill_questions:
        add_questions_column(conn, table_name)
        while True:
            empty_count, empty_ids = count_and_get_empty_questions(conn, table_name)
            max_id = get_row_count(conn, table_name)
            processed_rows = max_id - empty_count
            current_progress = processed_rows / max_id 
            print(f"Empty rows: {empty_count}\n")
            print(f"The progress: {current_progress:.2%}\n")
            if empty_count == 0 :
                break
            process_and_insert_questions(conn, "gpt-4o-mini", table_name, debug=debug, idList=empty_ids)
            if debug:
                break
            sys.stdout.flush() 
    if fill_topk_ranks:
        add_topk_rank_column(conn, table_name)
        while True:
            empty_count, empty_ids = count_and_get_empty_topk_rank(conn, table_name)
            max_id = get_row_count(conn, table_name)
            processed_rows = max_id - empty_count
            current_progress = processed_rows / max_id 
            print(f"Empty rows: {empty_count}\n")
            print(f"The progress: {current_progress:.2%}\n")
            if empty_count == 0:
                break
            add_topk_rank_result(conn, table_name, debug=debug, idList=empty_ids)
            if debug:
                break
            sys.stdout.flush() 

    conn.close()
    sys.exit(0)
    
