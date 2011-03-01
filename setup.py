from setuptools import find_packages, setup
import os

setup(
    name='django-catnap',
    description='REST framework for Django.',
    #long_description=open('README').read(),

     # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License"
    ],
    keywords='django app rest framework http',
    author='Alex Ehlke',
    author_email='alex.ehlke@gmail.com',
    url='http://github.com/aehlke/django-catnap',
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=[],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Django >= 1.3',
        'webob',
    ],
    #entry_points
)
