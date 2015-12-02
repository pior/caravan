from setuptools import setup, find_packages


setup(
    name='caravan',
    version='0.1.4',
    description='Light python framework for AWS SWF',
    long_description=open('README.rst').read(),
    keywords='AWS SWF workflow distributed background task',
    author='Pior Bastida',
    author_email='pior@pbastida.net',
    url='https://github.com/pior/caravan',
    license='MIT',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'boto3',
        'arrow',
        'six',
        'tabulate',
        ],
    extras_require={
        'dev': [
            'pytest',
            'pytest-mock',
            'pytest-cov',
            'zest.releaser[recommended]',
            'pylama',
            'pdbpp',
            'freezegun',
            ],
        },
    entry_points={
        'console_scripts': [
            'caravan-decider = caravan.commands.decider:Command.main',
            'caravan-start = caravan.commands.start:Command.main',
            'caravan-signal = caravan.commands.signal:Command.main',
            'caravan-terminate = caravan.commands.terminate:Command.main',
            'caravan-list = caravan.commands.list:Command.main',
            'caravan-domain-register = caravan.commands.domain_register:Command.main',
            ]
        },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Internet',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3.4',
        # 'Programming Language :: Python :: 3.5'
        ],
    )
