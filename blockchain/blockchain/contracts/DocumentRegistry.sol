// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DocumentRegistry {
    struct Document {
        uint256 timestamp;
        address issuerAddress;
        bool isAuthentic;
    }

    // Mapping from document hash to the document details
    mapping(bytes32 => Document) public documents;

    // Event emitted when a new document is anchored
    event DocumentAnchored(bytes32 indexed docHash, uint256 timestamp, address indexed issuerAddress, bool isAuthentic);
    // Event emitted when a tampered document is logged
    event TamperedDocumentDetected(bytes32 indexed docHash, uint256 timestamp, address indexed reporterAddress);

    /**
     * @dev Anchors an authentic document hash in the registry if not already anchored.
     * @param docHash The SHA-256 hash of the document.
     */
    function anchorDocument(bytes32 docHash) external {
        require(documents[docHash].timestamp == 0, "Document already anchored");
        
        uint256 currentTime = block.timestamp;
        
        documents[docHash] = Document({
            timestamp: currentTime,
            issuerAddress: msg.sender,
            isAuthentic: true
        });
        
        emit DocumentAnchored(docHash, currentTime, msg.sender, true);
    }

    /**
     * @dev Retrieves document details by hash.
     * @param docHash The SHA-256 hash of the document.
     * @return timestamp The timestamp when anchored, or 0.
     * @return issuerAddress The address that anchored the document.
     * @return isAuthentic The stored authenticity status.
     */
    function verifyDocument(bytes32 docHash) external view returns (uint256 timestamp, address issuerAddress, bool isAuthentic) {
        Document memory doc = documents[docHash];
        return (doc.timestamp, doc.issuerAddress, doc.isAuthentic);
    }
}
