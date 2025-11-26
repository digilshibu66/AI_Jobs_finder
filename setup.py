import setuptools

setuptools.setup(
    name='freelance_mailer',
    version='0.1.0',
    description='Automated freelance job scraper and mailer using Gemini',
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        'requests', 'beautifulsoup4', 'PyPDF2', 'faiss-cpu', 'google-generativeai'
    ],
    entry_points={
        'console_scripts': [
            'freelance-mailer=freelance_mailer.main:run'
        ]
    }
)
