from enum import Enum

class NodeLabel(str, Enum):
    """Neo4j Node Labels"""
    WORKSPACE = "Workspace"
    CONVERSATION = "Conversation"
    MESSAGE = "Message"
    DOCUMENT = "Document"
    ENTITY = "Entity"
    MEMO = "Memo"

class RelationshipType(str, Enum):
    """Neo4j Relationship Types"""
    CONTAINS = "CONTAINS"          # Workspace -> Conversation
    HAS_DOCUMENT = "HAS_DOCUMENT"  # Workspace -> Document
    HAS_MESSAGE = "HAS_MESSAGE"    # Conversation -> Message
    MENTIONS = "MENTIONS"          # Message/Document -> Entity
    REFERENCES = "REFERENCES"      # Memo -> Message/Document
    RELATED_TO = "RELATED_TO"      # Entity -> Entity
    NEXT_MESSAGE = "NEXT_MESSAGE"  # Message -> Message (Linked List)
