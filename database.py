import os
import requests

class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_KEY")
        
        print("🔍 SUPABASE_URL:", "✅" if self.url else "❌ NO EXISTE")
        print("🔍 SUPABASE_KEY:", "✅" if self.key else "❌ NO EXISTE")
        
        if not self.url or not self.key:
            raise Exception("❌ Faltan SUPABASE_URL o SUPABASE_KEY")
        
        print("✅ Cliente Supabase inicializado")
    
    def table(self, nombre):
        return SupabaseTable(self.url, self.key, nombre)


class SupabaseTable:
    def __init__(self, url, key, table_name):
        self.url = url
        self.key = key
        self.table_name = table_name
        self.params = []
    
    def select(self, columns):
        self.params.append(f"select={columns}")
        return self
    
    def eq(self, column, value):
        self.params.append(f"{column}=eq.{value}")
        return self
    
    def order(self, column, desc=False):
        self.params.append(f"order={column}.{'desc' if desc else 'asc'}")
        return self
    
    def execute(self):
        endpoint = f"{self.url}/rest/v1/{self.table_name}?" + "&".join(self.params)
        headers = {"apikey": self.key, "Authorization": f"Bearer {self.key}"}
        response = requests.get(endpoint, headers=headers)
        
        class Respuesta:
            def __init__(self, data):
                self.data = data
        
        if response.status_code == 200:
            return Respuesta(response.json())
        print(f"❌ Error API: {response.status_code} - {response.text}")
        return Respuesta([])
    
    def insert(self, data):
        endpoint = f"{self.url}/rest/v1/{self.table_name}"
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        response = requests.post(endpoint, headers=headers, json=data)
        
        class Respuesta:
            def __init__(self, data):
                self.data = data
        
        if response.status_code in [200, 201]:
            return Respuesta(response.json() if response.text else [])
        print(f"❌ Error Insert: {response.status_code} - {response.text}")
        return Respuesta([])
