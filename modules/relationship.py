import re

def getRelationship(question):
    # Create dictionaries mapping full language names and full years to their corresponding language codes and year values
    countries = ["Côte d'Ivoire", 'Vietnam', 'Nigeria', 'Zambia', 'Tanzania',
               'Rwanda', 'Haiti', 'Zimbabwe', 'Ethiopia', 'South Africa',
               'Guyana', 'Namibia', 'Botswana', 'Mozambique', 'Kenya',
               'Kazakhstan', 'Uganda', 'Kyrgyzstan', 'Senegal', 'Benin',
               'Lesotho', 'Pakistan', 'Swaziland', 'Ghana', 'Angola', 'Lebanon',
               'Sierra Leone', 'Cameroon', 'South Sudan', 'Burundi',
               'Dominican Republic', 'Malawi', 'Congo, DRC', 'Sudan', 'Mali',
               'Guatemala', 'Togo', 'Afghanistan', 'Liberia', 'Burkina Faso',
               'Guinea', 'Libya', 'Belize']
    countries = [x.lower() for x in countries]

    # Convert the question to lowercase for case-insensitive matching
    question_lower = question.lower()

    # Initialize variables to store language code and year value
    country = ""

    # Check if any language names are present in the question
    for vals in countries:
        if vals.lower() in question_lower:
            country = vals
            break

    # Construct the relationship string based on the presence of language and year in the question
    relationship = ""
    if country:
        relationship += f" and (pdt)-[:WEIGHT]->(:Country{{name:{country}}})"

    return relationship

    
