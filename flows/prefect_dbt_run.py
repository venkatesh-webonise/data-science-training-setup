from prefect import flow, task
from prefect.logging import get_run_logger
from prefect_dbt.cli.commands import DbtCoreOperation


# Configuration constants
DBT_PROJECT_DIR = "/usr/app/training_dbt"
DBT_PROFILES_DIR = "/usr/app"


@task
def run_dbt_seed(full_refresh: bool = False, seed_name: str | None = None):
    logger = get_run_logger()
    
    # Build the command
    command = ["dbt", "seed"]
    
    if full_refresh:
        command.append("--full-refresh")
    
    if seed_name:
        command.extend(["--select", seed_name])
    
    logger.info(f"Running command: {' '.join(command)}")
    
    # Execute the command using DbtCoreOperation
    result = DbtCoreOperation(
        commands=[command],
        project_dir=DBT_PROJECT_DIR,
        profiles_dir=DBT_PROFILES_DIR
    ).run()
    
    logger.info("dbt seed completed successfully")
    return result


@task
def run_dbt_models(model_selection: str | None = None):

    logger = get_run_logger()
    
    # Build the command
    command = ["dbt", "run"]
    
    if model_selection and model_selection != "*":
        # Split by space to handle multiple models
        models = model_selection.split()
        command.extend(["--select"] + models)
    
    logger.info(f"Running command: {' '.join(command)}")
    
    # Execute the command using DbtCoreOperation
    result = DbtCoreOperation(
        commands=[command],
        project_dir=DBT_PROJECT_DIR,
        profiles_dir=DBT_PROFILES_DIR
    ).run()
    
    logger.info("dbt run completed successfully")
    return result


@task
def run_dbt_tests(model_selection: str | None = None):
    logger = get_run_logger()
    
    # Build the command
    command = ["dbt", "test"]
    
    # If model_selection is provided and not '*', add --select with models
    if model_selection and model_selection != "*":
        # Split by space to handle multiple models
        models = model_selection.split()
        command.extend(["--select"] + models)
    
    logger.info(f"Running command: {' '.join(command)}")
    
    # Execute the command using DbtCoreOperation
    result = DbtCoreOperation(
        commands=[command],
        project_dir=DBT_PROJECT_DIR,
        profiles_dir=DBT_PROFILES_DIR
    ).run()
    
    logger.info("dbt test completed successfully")
    
    # Optional: Implement success heuristic
    # Check if the result indicates any test failures
    if hasattr(result, 'returncode') and result.returncode != 0:
        logger.error("dbt tests failed!")
        raise Exception(f"dbt test command failed with return code {result.returncode}")
    
    return result


@flow(name="dbt_flow_run", log_prints=True)
def prefect_dbt_flow_run(
    run_tests: bool = False,
    full_refresh: bool = False,
    seed_name: str | None = None,
    model_selection: str | None = None
):
    
    logger = get_run_logger()
    logger.info("=" * 60)
    logger.info("Starting dbt Flow Run")
    logger.info("=" * 60)
    logger.info(f"Parameters:")
    logger.info(f"  - run_tests: {run_tests}")
    logger.info(f"  - full_refresh: {full_refresh}")
    logger.info(f"  - seed_name: {seed_name}")
    logger.info(f"  - model_selection: {model_selection}")
    logger.info("=" * 60)
    
    results = {}
    
    # Step 1: Run dbt seed
    logger.info("Step 1: Running dbt seed...")
    results['seed'] = run_dbt_seed(full_refresh=full_refresh, seed_name=seed_name)
    
    # Step 2: Run dbt models
    logger.info("Step 2: Running dbt models...")
    results['run'] = run_dbt_models(model_selection=model_selection)
    
    # Step 3: Optionally run dbt tests
    if run_tests:
        logger.info("Step 3: Running dbt tests...")
        results['test'] = run_dbt_tests(model_selection=model_selection)
    else:
        logger.info("Step 3: Skipping dbt tests (run_tests=False)")
    
    logger.info("=" * 60)
    logger.info("dbt Flow Run completed successfully!")
    logger.info("=" * 60)
    
    return results


if __name__ == "__main__":
    prefect_dbt_flow_run()
