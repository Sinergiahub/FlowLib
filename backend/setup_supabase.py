#!/usr/bin/env python3
"""
Setup Supabase database schema for FlowLib
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

def main():
    # Get Supabase credentials
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file")
        sys.exit(1)
    
    print(f"🔗 Connecting to Supabase: {supabase_url}")
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Read schema file
        schema_file = ROOT_DIR / 'supabase_schema.sql'
        if not schema_file.exists():
            print(f"❌ Error: Schema file not found: {schema_file}")
            sys.exit(1)
        
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        print("📋 Executing schema setup...")
        
        # Execute schema (Supabase doesn't support direct SQL execution via Python client)
        # We'll need to execute this manually or use the RPC function
        print("⚠️  Please execute the SQL schema manually in Supabase SQL Editor:")
        print("1. Go to https://supabase.com/dashboard")
        print("2. Open SQL Editor")
        print("3. Copy and paste the contents of supabase_schema.sql")
        print("4. Click 'Run'")
        print(f"📁 Schema file location: {schema_file}")
        
        # Test connection by trying to fetch from a simple table
        try:
            result = supabase.table('categories').select('*').limit(1).execute()
            if result.data:
                print("✅ Schema already exists and connection successful!")
                return True
        except Exception as e:
            print(f"⚠️  Schema not yet created: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to Supabase: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()