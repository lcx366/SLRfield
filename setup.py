from setuptools import setup,find_packages 

setup(
    name='slrfield',
    version='0.2.0',
    description='A package to handle the SLR(Satellite Laser Ranging) data',
    author='Chunxiao Li',
    author_email='lcx366@126.com',
    url='https://github.com/lcx366/SLRfield',
    license='MIT',
    long_description_content_type='text/markdown',
    long_description=open('README.md', 'rb').read().decode('utf-8'),
    keywords=['SLR','CPF'],
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'scipy',
        'numpy>=1.21.2',
        'astropy>=4.3.1',
        'wget',
        'beautifulsoup4'
        ],
)
