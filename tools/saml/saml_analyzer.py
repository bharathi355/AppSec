import xml.etree.ElementTree as ET
import ssl
import socket
from urllib.parse import urlparse
import re

# -----------------------------------------------------------------------------
# Module for Recommendation 1: Ensuring Confidentiality (2.1)
# -----------------------------------------------------------------------------

def check_assertion_encryption(saml_assertion_xml):
    """
    Checks if the SAML assertion or specific attributes are encrypted.
    """
    try:
        root = ET.fromstring(saml_assertion_xml)
        # Define XML namespaces (adjust as needed for your SAML)
        namespaces = {
            'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
            'enc': 'http://www.w3.org/2001/04/xmlenc#',  # XML Encryption namespace
            # Add other relevant namespaces here
        }

        # Check for EncryptedAssertion element
        encrypted_assertion = root.find('.//enc:EncryptedAssertion', namespaces)
        if encrypted_assertion is not None:
            return "PASS: SAML assertion is encrypted."

        # Check for EncryptedAttribute elements within Attribute statements
        encrypted_attributes = root.findall('.//saml:Attribute/enc:EncryptedData', namespaces)
        if encrypted_attributes:
            return "PASS: Sensitive attributes are encrypted."

        # If no encryption is found, check for sensitive attributes (example: name, ssn)
        sensitive_attributes = []
        for attribute in root.findall('.//saml:Attribute', namespaces):
            attribute_name = attribute.get('Name')
            if attribute_name in ['name', 'ssn', 'medicalRecordNumber']:  # Example sensitive attributes
                sensitive_attributes.append(attribute_name)
        if sensitive_attributes:
            return f"WARNING: Sensitive attributes ({', '.join(sensitive_attributes)}) found without encryption."
        
        return "INFO: No explicit encryption detected.  Consider security at transport layer."

    except ET.ParseError:
        return "ERROR: Could not parse SAML assertion XML."
    except Exception as e:
        return f"ERROR: An unexpected error occurred: {e}"


def check_transport_layer_security(target_url):
    """
    Checks if the transport layer (TLS) is used appropriately.
    """
    try:
        parsed_url = urlparse(target_url)
        if parsed_url.scheme != 'https':
            return "FAIL: Transport layer security (HTTPS) is not used."

        hostname = parsed_url.hostname
        port = parsed_url.port if parsed_url.port else 443  # Default HTTPS port

        context = ssl.create_default_context()

        with socket.create_connection((hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                if not cert:
                    return "WARNING: No certificate found for the target URL."

                #Basic certificate validation (expiration)
                #TODO: Expand cert validation checks.
                return "PASS: Transport layer security (HTTPS) is used."

    except socket.gaierror as e:
        return f"ERROR: Could not resolve hostname: {e}"
    except ssl.SSLError as e:
        return f"ERROR: SSL error: {e}"
    except Exception as e:
        return f"ERROR: An unexpected error occurred: {e}"

# -----------------------------------------------------------------------------
# Module for Recommendation 2: Notes on Anonymity (2.2)
# -----------------------------------------------------------------------------

def analyze_identifying_attributes(saml_assertion_xml):
    """
    Identifies potentially identifying attributes within a SAML assertion.
    """
    try:
        root = ET.fromstring(saml_assertion_xml)
        namespaces = {
            'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
            # Add other relevant namespaces here
        }

        identifying_attributes = []
        for attribute in root.findall('.//saml:Attribute', namespaces):
            attribute_name = attribute.get('Name')
            #Add to or change list for what is considered an identifying attribute
            if attribute_name in ['email', 'username', 'employeeID', 'nameIdentifier']:
                identifying_attributes.append(attribute_name)

        if identifying_attributes:
            return f"WARNING: Potentially identifying attributes found: {', '.join(identifying_attributes)}"
        else:
            return "INFO: No commonly identifying attributes detected."

    except ET.ParseError:
        return "ERROR: Could not parse SAML assertion XML."
    except Exception as e:
        return f"ERROR: An unexpected error occurred: {e}"


def analyze_pseudonym_reuse(saml_assertion_xml): #This is a placeholder.  Real Implementation depends on knowing previous assertions.
    """
    Placeholder for pseudonym reuse analysis.  A real implementation would
    require tracking previous assertions and analyzing NameID values over time.
    """
    return "INFO: Pseudonym reuse analysis requires tracking assertions over time.  Implementation needed."

# -----------------------------------------------------------------------------
# Main execution (example usage)
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # Example SAML assertion (replace with your actual SAML)
    saml_assertion = """
    <saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" Version="2.0" ID="assertion1">
        <saml:Subject>
            <saml:NameID>user123</saml:NameID>
        </saml:Subject>
        <saml:AttributeStatement>
            <saml:Attribute Name="email" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
                <saml:AttributeValue>user@example.com</saml:AttributeValue>
            </saml:Attribute>
            <saml:Attribute Name="role" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
                <saml:AttributeValue>administrator</saml:AttributeValue>
            </saml:Attribute>
        </saml:AttributeStatement>
    </saml:Assertion>
    """

    print("--- Recommendation 1: Ensuring Confidentiality ---")
    encryption_result = check_assertion_encryption(saml_assertion)
    print(f"Assertion Encryption Check: {encryption_result}")

    target_url = "https://example.com/saml/acs"  # Replace with your actual ACS URL
    tls_result = check_transport_layer_security(target_url)
    print(f"Transport Layer Security Check: {tls_result}")

    print("\n--- Recommendation 2: Notes on Anonymity ---")
    identifying_attributes_result = analyze_identifying_attributes(saml_assertion)
    print(f"Identifying Attributes Analysis: {identifying_attributes_result}")

    pseudonym_reuse_result = analyze_pseudonym_reuse(saml_assertion)
    print(f"Pseudonym Reuse Analysis: {pseudonym_reuse_result}")
