from setuptools import setup, find_packages

version = '0.1'

setup(
    name='ckanext-statistics',
    version=version,
    description='NHM Stats plugin.',
    long_description='',
    classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Ben Scott',
    author_email='ben@benscott.co.uk',
    url='',
    license='',
    packages=find_packages(exclude=['ez_setup', 'stats', 'tests']),
    namespace_packages=['ckanext', 'ckanext.statistics'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    entry_points= \
        """
            [ckan.plugins]
            statistics=ckanext.statistics.plugin:StatisticsPlugin
            [paste.paster_command]
            stats=ckanext.statistics.commands.stats:StatsCommand
        """,
)
