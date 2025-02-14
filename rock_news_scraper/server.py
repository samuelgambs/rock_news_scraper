from fastapi import FastAPI
import subprocess

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Rock News Scraper está rodando!"}

@app.get("/run-scraper")
def run_scraper():
    try:
        # Chama seu script diretamente
        result = subprocess.run(["python", "main.py"], capture_output=True, text=True)
        return {"status": "success", "output": result.stdout}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
