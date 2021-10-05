# Beautiful Portfolio Tools

## What it is
The Beautiful Portfolio Tools are a refactoring of [RAutoInvest](https://github.com/ProbStub/RAutoInvest),
an abandoned attempt at a robo-advisor venture six years ago.
Since then, I have picked up Python and like to put my investment tools on more solid grounds.
Use at your own risk—no investment advice.

## How to run
Presently the refactoring is focused on the data load and portfolio construction logic.
You will need access to Kubernetes (either local minikube or at your preferred cloud provider)
to run PySpark and PostgreSQL. Other than that the following should get you started:

0. (Optional) create a new conda environment by running ```conda create -n bpt_conda```
1. Ensure all dependencies are installed ````pip install -r requirements.txt````
2. PySpark needs to be installed locally for code to execute
3. Insert your database, cloud and API secrets into the ```.env``` file
4. Run ````python main.py```` in the repos root directory (this directory)

If you need more detailed instructions have a look at the [manifest README](manifests/README.md)
which walks through some steps in more details (but is presently work in progress).

## How to contribute
The code is public for a reason, and if you like to contribute, please consider to:
- Provide test_* files for your contribution
- Ensure that linting completes without issues

To set up your development environment after cloning the repo please perform the following preparation steps:
1. Pre-Commit hooks have been established so please run ````pre-commit install````
2. PyTests are located in the ```/test``` directory but excluded from pre-commit hooks. Uncomment the testing hook in
   ````.pre-commit-config.yaml```` if you wish to enable pre-commit tests
3. Very basic linting is configured in ````.pylintrc````, adapt as needed
4. Secrets can be maintained in ```.env``` and ````.gitignore```` is ignoring that file

> NOTE: pre-commit hooks to trim whitespaces are defined and may fail at the first commit. Check the logs and try again.

## Some background
I have created [RAutoInvest](https://github.com/ProbStub/RAutoInvest) initially to demonstrate the feasibility of
automated ETF investments with relatively simple tooling. The objective has been to acquire funding for a
robo-advisor venture but the project did not succeed.
There had been discussions to improve the codebase and donate to an investor protection site.
The aim has been to screen portfolio proposals for hidden fees. However, life intervened, and
I could not go ahead with that project.
The technology looks outdated years later, but I still find myself needing portfolio
tooling and having a bit of time on my hands. Hence, I am picking up this refactoring project as a
hobby, applying some tricks acquired over the years. That said, it is a hobby; issue response and commits may be
intermittent.

Refactoring will initially focus on the following:
- Change the data load to PySpark pipelines
- Leverage ML facilities for data correction and imputation
- Provide a Kubernetes run-time environment
- Establish a testing and basic CI/CD setup
- Switch to Python tooling for portfolio construction and performance evaluation

Later objectives will include:
- Building a user interface beyond the command line interface
- Provision broker connectivity facilities
- Extend portfolio construction to emerging ML facilitated strategies
