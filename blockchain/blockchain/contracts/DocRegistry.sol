// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DocRegistry {
    // Mapping from document hash to the timestamp it was anchored
    mapping(bytes32 => uint256) public documentTimestamps;

    // Event emitted when a new document is anchored
    event DocumentAnchored(bytes32 indexed docHash, uint256 timestamp);

    /**
     * @dev Anchors a document hash in the registry.
     * @param docHash The SHA-256 hash of the document.
     */
    function anchorDocument(bytes32 docHash) external {
        require(documentTimestamps[docHash] == 0, "Document already anchored");
        
        uint256 currentTime = block.timestamp;
        documentTimestamps[docHash] = currentTime;
        
        emit DocumentAnchored(docHash, currentTime);
    }

    /**
     * @dev Verifies if a document hash has been anchored.
     * @param docHash The SHA-256 hash of the document.
     * @return The timestamp when the document was anchored (0 if not anchored).
     */
    function verifyDocument(bytes32 docHash) external view returns (uint256) {
        return documentTimestamps[docHash];
    }
}
