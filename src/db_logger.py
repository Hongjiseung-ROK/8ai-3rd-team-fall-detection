import pyodbc
import datetime
import os

class AzureDBLogger:
    def __init__(self, env_path='sql.env'):
        self.conn_str = self._get_connection_string(env_path)
        self.connected = False
        try:
             # Test connection
            with pyodbc.connect(self.conn_str) as conn:
                self.connected = True
                print("[DB] Connection check successful.")
        except Exception as e:
            print(f"[DB] Initial connection check failed: {e}")
            print("Make sure your IP is allowed in Azure SQL Server Firewall rules.")

    @staticmethod
    def get_config(key, env_path='sql.env'):
        # 1. Try to read from file
        paths_to_check = [env_path, os.path.join('..', env_path), os.path.join('c:\\workspace\\marker_dev', env_path)]
        
        found_path = None
        for p in paths_to_check:
            if os.path.exists(p):
                found_path = p
                break
        
        val = None
        if found_path:
            try:
                with open(found_path, 'r') as f:
                    for line in f:
                        if '=' in line:
                            parts = line.split('=', 1)
                            k = parts[0].strip()
                            v = parts[1].strip().strip('"').strip("'")
                            if k == key:
                                val = v
                                break
            except Exception as e:
                print(f"[Config] Warning: Could not read {found_path}: {e}")
        return val

    def _get_connection_string(self, env_path):
        # 1. Get props from file
        base_str = AzureDBLogger.get_config('sql_ocbc', env_path)
        password = AzureDBLogger.get_config('sql_pw', env_path)

        # Remove hardcoded fallbacks
        if not base_str or not password:
            print("[DB] CRITICAL: 'sql_ocbc' or 'sql_pw' not found in sql.env.")
            print("Please create sql.env with valid credentials.")
            return ""

        # 3. Handle Driver Selection
        import pyodbc
        available_drivers = pyodbc.drivers()
        print(f"[DB] Available ODBC Drivers: {available_drivers}")
        
        # Check if the configured driver exists
        target_driver = "ODBC Driver 18 for SQL Server"
        if "Driver={" in base_str:
             try:
                 start = base_str.find("{") + 1
                 end = base_str.find("}")
                 target_driver = base_str[start:end]
             except:
                 pass

        if target_driver not in available_drivers:
            print(f"[DB] Warning: Configured driver '{target_driver}' not found.")
            priority = [
                "ODBC Driver 18 for SQL Server",
                "ODBC Driver 17 for SQL Server",
                "ODBC Driver 13 for SQL Server",
                "SQL Server Native Client 11.0",
                "SQL Server"
            ]
            
            selected_driver = None
            for d in priority:
                if d in available_drivers:
                    selected_driver = d
                    print(f"[DB] Using fallback driver: '{selected_driver}'")
                    break
            
            if selected_driver:
                if "Driver={" in base_str:
                    import re
                    base_str = re.sub(r"Driver={.*?};", f"Driver={{{selected_driver}}};", base_str)
                else:
                    base_str = f"Driver={{{selected_driver}}};" + base_str
            else:
                 print("[DB] Critical: No suitable SQL Server ODBC driver found. Connection will likely fail.")

        # 4. Inject Password
        if '{your_password_here}' in base_str:
            conn_str = base_str.replace('{your_password_here}', password)
        else:
            conn_str = base_str

        return conn_str

    def log_event(self, camera_id, angle, status, experiment_id=None):
        try:
            with pyodbc.connect(self.conn_str) as conn:
                cursor = conn.cursor()
                
                # Updated Query to include ExperimentID
                # Note: VerificationStatus is handled by DB DEFAULT
                query = """
                INSERT INTO FallEvents (CameraID, RiskAngle, Status, Timestamp, ExperimentID)
                VALUES (?, ?, ?, ?, ?)
                """
                current_time = datetime.datetime.now()
                
                # Pass experiment_id (can be None, resulting in NULL in DB)
                cursor.execute(query, (camera_id, angle, status, current_time, experiment_id))
                conn.commit()
                print(f"[DB Success] Event Saved: {status} ({int(angle)}deg)")
                
        except Exception as e:
            print(f"[DB Error] Failed to log event: {e}")
            # Optional: Attempt simpler reconnect or logging logic here

if __name__ == "__main__":
    # Test
    logger = AzureDBLogger()
    logger.log_event("TEST_CAM", 10.0, "TEST_MSG")
