# GOB Playground
The GOB Playground is for testing architetorial issues in the GOB project

Requirements:
- Python >=3.6

Installation:
- python3 -m venv venv
- source venv/bin/activate
- cd src
- pip install -r requirements.txt

For simplicity reasons no database is used, all logic operates on text and json files.
Results and intermediate results are easily inspected and discussed.

In the src directory you will find the following Python modules:
- reader
- processor
- writer

The reader reads input data.
The task of a reader (one per GOB input) is to:
- Read the input source data (this might need DB access, certificates, ftp transfer, ...)
- Process the input data and convert it to GOB format
- Write it to an output channel (persistent queue, database, ...)

The generic processor derives mutations from any GOB input.
The task of the processor is:
- Read any GOB data
- Process this data by comparing it to the current data and derive corresponding mutations
- Write it to an output channel (persistent queue, database, ...)

The generic writer updates the current data on the basis of mutations.
The task of the writer is:
- Read any mutations
- Process the mutations by updating the current data and registering the corresponding timestamps
- Write the data so that it becomes the new current data

The modules follow an orthogonal design.
Each module is structured identical to the main structure; reader, processor and writer.

To reinitialize the modules:
- copy the reader/original_data to reader/input_data
- copy the writer/original_data to writer/data

To run the modules:
- cd src/reader; python main.py
- cd src/processor; python main.py
- cd src/writer; python main.py

Alternatively a small shell script is available:
- cd src
- sh run.sh --clean
- sh run.sh

