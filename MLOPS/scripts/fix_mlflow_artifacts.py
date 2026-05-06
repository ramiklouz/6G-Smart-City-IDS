from pathlib import Path
import os
import sqlite3

DB_PATH = Path(__file__).resolve().parents[1] / "mlflow.db"
EXPERIMENT_NAME = os.environ.get("MLFLOW_EXPERIMENT_NAME", "6G_IDS_LightGBM")
PROXY_ARTIFACT_LOCATION = "mlflow-artifacts:/"


def main():
    if not DB_PATH.exists():
        raise SystemExit(f"MLflow database not found: {DB_PATH}")

    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT experiment_id, artifact_location FROM experiments WHERE name = ?",
            (EXPERIMENT_NAME,),
        ).fetchone()

        if row is None:
            print(f"No experiment named {EXPERIMENT_NAME!r} found yet.")
            print("Start MLflow and run training once, or create the experiment from MLflow UI.")
            return

        experiment_id, artifact_location = row
        if str(artifact_location).startswith("mlflow-artifacts:"):
            print(f"[OK] Experiment {EXPERIMENT_NAME!r} already uses UI-visible artifacts.")
            return

        conn.execute(
            "UPDATE experiments SET artifact_location = ? WHERE experiment_id = ?",
            (PROXY_ARTIFACT_LOCATION, experiment_id),
        )
        conn.commit()

    print(f"[OK] Updated {EXPERIMENT_NAME!r} artifact root for future runs.")
    print("Restart MLflow, then run make train-all again.")


if __name__ == "__main__":
    main()
