from setuptools import setup, find_packages

setup(
    name="examplerepo",
    packages=find_packages(exclude=["tests", "tests.*"]),
    setup_requires=["wheel"],
    version="0.1.0rc1",
    description="examplerepo",
    author="",
    entry_points={
        "console_scripts": [
            "etl = examplerepo.tasks.sample_etl_task:entrypoint",
            "model = examplerepo.tasks.sample_ml_task:entrypoint",
        ]
    },
)
