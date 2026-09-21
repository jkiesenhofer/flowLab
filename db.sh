#!/bin/bash

DB_FILE="flotation_simulation.db"
URL="http://jkiesenhofer.bplaced.net/db/flotation_simulation.db"

# 1. Download the database file if it isn't already local
if [ ! -f "$DB_FILE" ]; then
    echo "Downloading database from $URL..."
    wget -q "$URL" -O "$DB_FILE"
    echo "Download complete."
else
    echo "Database file '$DB_FILE' already exists locally."
fi

# 2. Run SQLite queries
echo "-----------------------------------"
echo "Executing SQLite queries..."
echo "-----------------------------------"

sqlite3 "$DB_FILE" <<EOF
-- Enable column headers and neat column formatting
.mode column
.headers on

-- Show all tables in the database
.tables

-- View the schema of the simulation_data table
.schema simulation_data

-- Show a preview of the dataset (limited to avoid terminal flooding)
SELECT * FROM simulation_data LIMIT 2000;
EOF
