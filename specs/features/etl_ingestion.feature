Feature: Document ETL Ingestion
  As an Architect
  I want to convert PDF documents into a structured Knowledge Graph
  In order to allow agents to reason over project requirements

  Scenario: Successfully ingest a technical specification PDF
    Given a technical PDF document "CdC_MBDA.pdf"
    When the ETLMapper processes the file
    Then it should extract text chunks for each page
    And it should identify technical entities like "LMS" or "Python"
    And it should store exactly 12 pages in the "Chunks" collection
    And the ArangoDB graph should reflect the document structure