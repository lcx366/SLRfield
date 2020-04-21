import setuptools
from setuptools import setup 

setup(
    name='slrfield',
    version='0.0.1',
    long_description_content_type='text/markdown',
    description='A package to handle the SLR(Satellite Laser Ranging) data',
    long_description=open('README.md', 'rb').read().decode('utf-8'),
    license='MIT',
    author='Chunxiao Li',
    author_email='lcx366@126.com',
    url='https://github.com/lcx366/SLRfield',
    classifiers=[
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        ],
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        'scipy',
        'numpy',
        'astropy'
        ],
)