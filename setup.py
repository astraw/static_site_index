from distutils.core import setup

setup(name='static_site_index',
      version='0.1.0',
      packages=['static_site_index',
                ],
      url='https://github.com/astraw/static_site_index',
      author='Andrew Straw',
      author_email='strawman@astraw.com',
      package_data={ 'static_site_index': ['*.js','*.html'],
                     },
      )
