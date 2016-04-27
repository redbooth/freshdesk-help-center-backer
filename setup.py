#!/usr/bin/env python
import setuptools


with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()
    requirements = [x for x in requirements if not x.startswith('#')]


setuptools.setup(
    name='freshdesk-help-center-backer',
    version='0.1',
    description='A Freshdesk help center backer written in Python',
    long_description='A Freshdesk help center backer written in Python',
    keywords='freshdesk,solution,help center,knowledge base',
    author='AeroFS',
    author_email='oss@aerofs.com',
    url='https://github.com/aerofs/freshdesk-help-center-backer',
    packages=['freshdesk', 'freshdesk.scripts', 'freshdesk.API'],
    entry_points={
        'console_scripts': [
            'freshdesk-deploy = freshdesk.deploy:main',
            'freshdesk-new = freshdesk.create_new_post_shell:main',
            'freshdesk-track = freshdesk.track_changes:main'
        ]
    },
    install_requires=requirements,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
)