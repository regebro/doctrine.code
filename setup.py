from setuptools import setup, find_packages

version = '0.1'

with open('README.rst', 'rt') as readme:
    description = readme.read()

with open('CHANGES.txt', 'rt') as changes:
    history = changes.read()

setup(name='doctrine.code',
      version=version,
      description="Lazy code wrapper with editing, analysis and "
                  "highlighting support",
      long_description=description + '\n' + history,
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.4',
                   'License :: OSI Approved :: MIT License',
                   'Topic :: Text Editors',
                   ],
      keywords='code editing display',
      author='Lennart Regebro',
      author_email='regebro@gmail.com',
      url='https://github.com/regebro/doctrine.code',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      test_suite='tests',
      install_requires=[
      ],
      )
