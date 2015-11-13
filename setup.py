from setuptools import find_packages
from setuptools import setup


setup(
    name='caravan',
    version='0.0.2',
    description='Light python framework for AWS SWF',
    long_description=open('README.rst').read(),
    keywords='AWS SWF workflow distributed background task',
    author='Pior Bastida',
    author_email='pior@pbastida.net',
    url='https://github.com/pior/caravan',
    license='MIT',
    packages=find_packages(),
    zip_safe=False,
    install_requires=['boto3'],
    extras_require={
        'dev': ['zest.releaser[recommended]'],
        },
    entry_points={
        "console_scripts": [
            "caravan-decider = caravan.commands.decider:Command.main",
            "caravan-start = caravan.commands.start:Command.main",
            "caravan-signal = caravan.commands.signal:Command.main",
            ]
        },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Programming Language :: Python :: 2.7",
        # "Programming Language :: Python :: 3.4",
        # "Programming Language :: Python :: 3.5"
        ],
    )
