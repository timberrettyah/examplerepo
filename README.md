# ah-sa-examplerepo

This is a sample project for Databricks, generated via cookiecutter.

While using this project, you need Python 3.X and `pip` or `conda` for package management.

## Local environment setup

1. Instantiate a local Python environment via a tool of your choice. This example is based on `conda`, but you can use any environment management tool:
```bash
conda create --name examplerepo --file requirements.txt python=3.9
conda activate examplerepo
```

2. Install all the other requirements using pip
```bash
conda config --set pip_interop_enabled True
pip install dbConnect databricks-cli dbx
pip install delta-spark --no-deps
pip install mlflow
```

3. Install project in a dev mode (this will also install dev requirements):
```bash
pip install -e ".[dev]"
```
## Add files to git

To add all the files to git, please use:
```bash
git init
git add .
```

## Check code quality

To perform linting and validation of the general code quality, please use:
```bash
Make format
```

In case of format errors (sometimes Pycharm introduces format errors), please re-run:
```bash
Make format
```

## Running unit tests

To trigger a single unit test, please use `pytest`:
```
pytest tests/unit --cov
```

To trigger all unit tests, please use `Make test-only`:
```
Make test-only
```

Please check the directory `tests/unit` for more details on how to use unit tests.
In the `tests/unit/conftest.py` you'll also find useful testing primitives, such as local Spark instance with Delta support, local MLflow and DBUtils fixture.

## Running entire pre-commit flow

To trigger all unit tests, linting and validation of the general code quality, please use `Make test`:
```
Make test
```

## Clean up pyc and caches

To clean up pyc and caches, please use `Make clean`:
```
Make clean
```

## Running integration tests

There are two options for running integration tests:

- On an interactive cluster via `dbx execute`
- On a job cluster via `dbx launch`

For quicker startup of the job clusters we recommend using instance pools ([AWS](https://docs.databricks.com/clusters/instance-pools/index.html), [Azure](https://docs.microsoft.com/en-us/azure/databricks/clusters/instance-pools/), [GCP](https://docs.gcp.databricks.com/clusters/instance-pools/index.html)).

For an integration test on interactive cluster, use the following command:
```
dbx execute --cluster-name=<name of interactive cluster> --job=<name of the job to test>
```

To execute a task inside multitask job, use the following command:
```
dbx execute \
    --cluster-name=<name of interactive cluster> \
    --job=<name of the job to test> \
    --task=<task-key-from-job-definition>
```

For a test on an automated job cluster, deploy the job files and then launch:
```
dbx deploy --jobs=<name of the job to test> --files-only
dbx launch --job=<name of the job to test> --as-run-submit --trace
```

Please note that for testing we recommend using [jobless deployments](https://dbx.readthedocs.io/en/latest/run_submit.html), so you won't affect existing job definitions.

## Interactive execution and development on Databricks clusters

1. `dbx` expects that cluster for interactive execution supports `%pip` and `%conda` magic [commands](https://docs.databricks.com/libraries/notebooks-python-libraries.html).
2. Please configure your job in `conf/deployment.yml` file.
2. To execute the code interactively, provide either `--cluster-id` or `--cluster-name`.
```bash
.dbx execute \
    --cluster-name="<some-cluster-name>" \
    --job=job-name
```

Multiple users also can use the same cluster for development. Libraries will be isolated per each execution context.

## Working with notebooks and Repos

To start working with your notebooks from a Repos, do the following steps:

1. Add your git provider token to your user settings
2. Add your repository to Repos. This could be done via UI, or via CLI command below:
```bash
databricks repos create --url <your repo URL> --provider <your-provider>
```
This command will create your personal repository under `/Repos/<username>/lightgbm_template`.
3. To set up the CI/CD pipeline with the notebook, create a separate `Staging` repo:
```bash
databricks repos create --url <your repo URL> --provider <your-provider> --path /Repos/Staging/examplerepo
```

## CI/CD pipeline settings

### Using [Personal Access Tokens](https://docs.databricks.com/dev-tools/api/latest/authentication.html) (PAT)

The Databricks CLI needs to be configured by correctly settting the following secrets or environment variables:
- `DATABRICKS_HOST`: The link to the desired workspace
- `DATABRICKS_TOKEN`: The PAT, should *always* be stored in a GitHub secret

Once set in your current environment, interaction through the Databricks CLI should work.

### Using a [Service Principal](https://docs.microsoft.com/en-us/azure/active-directory/develop/app-objects-and-service-principals)

A Service Principal is generally used to allow your application to authenticate with the Azure Active Directory, and
would therefore be able to reach certain resources it requires.
Before you can use a service principal, you must create one in the Azure portal. For more information, see [Create an Azure service principal with the Azure portal](https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal). Assuming you have created a service principal, you can use the following environment variables to configure the Databricks CLI:

- `AZURE_CLIENT_ID`: The application ID of the service principal
- `AZURE_TENANT_ID`: The tenant ID of the service principal
- `AZURE_SUBSCRIPTION_ID`: The subscription ID of the service principal
- `DATABRICKS_HOST`: The link to the desired workspace, e.g. `https://adb-1234567891234567.12.azuredatabricks.net`
- `DATABRICKS_RESOURCE_ID`: 2ff814a6-3304-4ab8-85cb-cd0e6f879c1d (this is a static resource ID of the Databricks workspace)

To authenticate using the service principal inside a CI/CD workflow in GitHub Actions, it is required to do 2 things:

- Create an environment in your GitHub repository under Settings -> Environments -> New environment and set it to a name of your choice, e.g. `production`

- Create a Federated Credential from the 'Certificates & secrets' tab in the Azure portal page for the service principal. Set the values as follows:
    - `Federated credential scenario`: GitHub Actions deploying Azure resources
    - `Organization`: RoyalAholdDelhaize
    - `Repository`: >your-repo-name<
    - `Entity type`: Environment
    - `GitHub environment name`: >your-environment-name<, e.g. 'production'
    - `Name`: A unique name for the credential, e.g. >your-repo-name<+>your-environment-name<


Be aware that inside a job definition in a workflow file, you must activate your GitHub environment using
`environment: >your-environment-name<` Using the following steps in a GitHub Actions workflow your databricks CLI
should be authenticated correctly, enabling you to deploy your job definitions to Databricks:


```yaml
- name: Azure CLI login
  uses: azure/login@v1
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

```yaml
- name: Configure databricks CLI
  env:
    DATABRICKS_RESOURCE_ID: 2ff814a6-3304-4ab8-85cb-cd0e6f879c1d
  run: |
    export DATABRICKS_AAD_TOKEN=$(az account get-access-token --resource ${{ env.DATABRICKS_RESOURCE_ID }} | jq -r .accessToken)
    databricks configure --aad-token --host ${{ secrets.DATABRICKS_HOST }}
```


An example of a full workflow file can be found [here](.github/workflows/azure_login.yml). This workflow can be run
manually by clicking the 'Run workflow' button in the Actions tab of your repository.

## Testing and releasing via CI pipeline

- To trigger the CI pipeline, simply push your code to the repository. If CI provider is correctly set, it shall trigger the general testing pipeline
- To trigger the release pipeline, get the current version from the `lightgbm_template/__init__.py` file and tag the current code version:
```
git tag -a v<your-project-version> -m "Release tag for version <your-project-version>"
git push origin --tags
```
