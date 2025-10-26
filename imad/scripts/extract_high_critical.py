raw_text = """
    [HIGH] gomodules: Denial of Service (DoS)
    [MEDIUM] gomodules: Incorrect Privilege Assignment
    [LOW] maven: Server-side Request Forgery (SSRF)
    [MEDIUM] maven: Improper Neutralization of Special Elements
    [MEDIUM] maven: Improper Neutralization of Special Elements
    [HIGH] maven: Server-side Request Forgery (SSRF)
    [HIGH] maven: Deserialization of Untrusted Data
    [HIGH] maven: Deserialization of Untrusted Data
    [MEDIUM] maven: Files or Directories Accessible to External Parties
    [HIGH] maven: Incorrect Implementation of Authentication Algorithm
    [MEDIUM] maven: Improper Handling of Case Sensitivity
    [HIGH] maven: Allocation of Resources Without Limits or Throttling
    [MEDIUM] maven: Authentication Bypass Using an Alternate Path or Channel
    [HIGH] maven: Integer Overflow or Wraparound
    [HIGH] maven: Allocation of Resources Without Limits or Throttling
    [MEDIUM] maven: Session Fixation
    [HIGH] maven: Improper Resource Shutdown or Release
    [HIGH] maven: Insufficient Session Expiration
    [HIGH] maven: Allocation of Resources Without Limits or Throttling
    [CRITICAL] maven: Uncaught Exception
    [CRITICAL] maven: Time-of-check Time-of-use (TOCTOU) Race Condition
    [CRITICAL] maven: Time-of-check Time-of-use (TOCTOU) Race Condition
    [HIGH] maven: Path Equivalence
    [HIGH] maven: Improper Cleanup on Thrown Exception
    [MEDIUM] maven: Improper Neutralization
    [LOW] maven: Improper Handling of Case Sensitivity
    [LOW] maven: Improper Handling of Case Sensitivity
    [MEDIUM] maven: HTTP Response Splitting
    [HIGH] maven: Open Redirect
    [MEDIUM] maven: Open Redirect
    [MEDIUM] maven: Denial of Service (DoS)
    [LOW] maven: Improper Handling of Case Sensitivity
    [HIGH] maven: Relative Path Traversal
    [HIGH] maven: Incorrect Authorization
    [LOW] maven: Improper Handling of Case Sensitivity
    [HIGH] maven: Path Traversal
    [LOW] maven: Improper Handling of Case Sensitivity
    [HIGH] maven: Path Traversal
    [LOW] maven: Server-side Request Forgery (SSRF)
    [MEDIUM] maven: Improper Neutralization of Special Elements
    [MEDIUM] maven: Improper Neutralization of Special Elements
    [HIGH] maven: Server-side Request Forgery (SSRF)
    [HIGH] maven: Deserialization of Untrusted Data
    [HIGH] maven: Deserialization of Untrusted Data
    [MEDIUM] maven: Files or Directories Accessible to External Parties
    [HIGH] maven: Incorrect Implementation of Authentication Algorithm
    [MEDIUM] maven: Improper Handling of Case Sensitivity
    [HIGH] maven: Allocation of Resources Without Limits or Throttling
    [MEDIUM] maven: Authentication Bypass Using an Alternate Path or Channel
    [HIGH] maven: Integer Overflow or Wraparound
    [HIGH] maven: Allocation of Resources Without Limits or Throttling
    [MEDIUM] maven: Session Fixation
    [HIGH] maven: Improper Resource Shutdown or Release
    [CRITICAL] maven: Uncaught Exception
    [CRITICAL] maven: Time-of-check Time-of-use (TOCTOU) Race Condition
    [CRITICAL] maven: Time-of-check Time-of-use (TOCTOU) Race Condition
    [HIGH] maven: Path Equivalence
    [HIGH] maven: Improper Cleanup on Thrown Exception
    [MEDIUM] maven: Improper Neutralization
    [LOW] maven: Improper Handling of Case Sensitivity
    [LOW] maven: Improper Handling of Case Sensitivity
    [MEDIUM] maven: HTTP Response Splitting
    [MEDIUM] maven: Denial of Service (DoS)
    [LOW] maven: Improper Handling of Case Sensitivity
    [HIGH] maven: Relative Path Traversal
    [HIGH] maven: Incorrect Authorization
    [LOW] maven: Improper Handling of Case Sensitivity
    [HIGH] maven: Path Traversal
    [LOW] maven: Improper Handling of Case Sensitivity
    [HIGH] maven: Path Traversal
    [LOW] maven: Server-side Request Forgery (SSRF)
    [MEDIUM] maven: Improper Neutralization of Special Elements
    [MEDIUM] maven: Improper Neutralization of Special Elements
    [HIGH] maven: Server-side Request Forgery (SSRF)
    [HIGH] maven: Deserialization of Untrusted Data
    [HIGH] maven: Deserialization of Untrusted Data
    [MEDIUM] maven: Files or Directories Accessible to External Parties
    [HIGH] maven: Incorrect Implementation of Authentication Algorithm
    [MEDIUM] maven: Improper Handling of Case Sensitivity
    [HIGH] maven: Allocation of Resources Without Limits or Throttling
    [MEDIUM] maven: Authentication Bypass Using an Alternate Path or Channel
    [HIGH] maven: Integer Overflow or Wraparound
    [HIGH] maven: Allocation of Resources Without Limits or Throttling
    [MEDIUM] maven: Session Fixation
    [HIGH] maven: Improper Resource Shutdown or Release
    [CRITICAL] maven: Uncaught Exception
    [CRITICAL] maven: Time-of-check Time-of-use (TOCTOU) Race Condition
    [CRITICAL] maven: Time-of-check Time-of-use (TOCTOU) Race Condition
    [HIGH] maven: Path Equivalence
    [HIGH] maven: Improper Cleanup on Thrown Exception
    [MEDIUM] maven: Improper Neutralization
    [LOW] maven: Improper Handling of Case Sensitivity
    [LOW] maven: Improper Handling of Case Sensitivity
    [MEDIUM] maven: HTTP Response Splitting
    [MEDIUM] maven: Denial of Service (DoS)
    [LOW] maven: Improper Handling of Case Sensitivity
    [HIGH] maven: Relative Path Traversal
    [HIGH] maven: Incorrect Authorization
    [LOW] maven: Improper Handling of Case Sensitivity
    [HIGH] maven: Path Traversal
    [LOW] maven: Improper Handling of Case Sensitivity
    [HIGH] maven: Path Traversal
    [MEDIUM] maven: Improper Input Validation
    [HIGH] gomodules: Directory Traversal
    [HIGH] gomodules: Access Restriction Bypass
    [MEDIUM] gomodules: Denial of Service (DoS)
    [MEDIUM] gomodules: Denial of Service (DoS)
    [MEDIUM] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [MEDIUM] gomodules: Improper Verification of Cryptographic Signature
    [MEDIUM] gomodules: Improper Verification of Cryptographic Signature
    [MEDIUM] gomodules: Authentication Bypass by Capture-replay
    [CRITICAL] gomodules: Incorrect Implementation of Authentication Algorithm
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [MEDIUM] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [MEDIUM] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [MEDIUM] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [MEDIUM] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [MEDIUM] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [MEDIUM] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [MEDIUM] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [MEDIUM] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [MEDIUM] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [MEDIUM] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [MEDIUM] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [MEDIUM] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [MEDIUM] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [MEDIUM] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [MEDIUM] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [MEDIUM] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [MEDIUM] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [MEDIUM] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [MEDIUM] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [MEDIUM] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [MEDIUM] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [MEDIUM] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [MEDIUM] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [MEDIUM] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [MEDIUM] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [MEDIUM] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [MEDIUM] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [MEDIUM] gomodules: Incorrect Privilege Assignment
    [MEDIUM] gomodules: Incorrect Privilege Assignment
    [MEDIUM] gomodules: Incorrect Privilege Assignment
    [MEDIUM] gomodules: Incorrect Privilege Assignment
    [MEDIUM] gomodules: Incorrect Privilege Assignment
    [MEDIUM] gomodules: Incorrect Privilege Assignment
    [MEDIUM] gomodules: Incorrect Privilege Assignment
    [MEDIUM] gomodules: Incorrect Privilege Assignment
    [MEDIUM] gomodules: Incorrect Privilege Assignment
    [MEDIUM] gomodules: Incorrect Privilege Assignment
    [MEDIUM] gomodules: Incorrect Privilege Assignment
    [MEDIUM] gomodules: Incorrect Privilege Assignment
    [MEDIUM] gomodules: Incorrect Privilege Assignment
    [MEDIUM] gomodules: Incorrect Privilege Assignment
    [MEDIUM] gomodules: Incorrect Privilege Assignment
    [MEDIUM] gomodules: Incorrect Privilege Assignment
    [MEDIUM] gomodules: Incorrect Privilege Assignment
    [MEDIUM] gomodules: Incorrect Privilege Assignment
    [MEDIUM] gomodules: Incorrect Privilege Assignment
    [MEDIUM] gomodules: Incorrect Privilege Assignment
    [MEDIUM] gomodules: Incorrect Privilege Assignment
    [MEDIUM] gomodules: Incorrect Privilege Assignment
    [MEDIUM] gomodules: Incorrect Privilege Assignment
    [MEDIUM] gomodules: Incorrect Privilege Assignment
    [MEDIUM] gomodules: Incorrect Privilege Assignment
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: NULL Pointer Dereference
    [MEDIUM] gomodules: Information Exposure
    [MEDIUM] gomodules: Path Traversal
    [MEDIUM] gomodules: Path Traversal
    [MEDIUM] gomodules: Path Traversal
    [MEDIUM] gomodules: Path Traversal
    [MEDIUM] gomodules: Path Traversal
    [MEDIUM] gomodules: Path Traversal
    [MEDIUM] gomodules: Path Traversal
    [MEDIUM] gomodules: Path Traversal
    [MEDIUM] gomodules: Path Traversal
    [MEDIUM] gomodules: Path Traversal
    [MEDIUM] gomodules: Path Traversal
    [MEDIUM] gomodules: Path Traversal
    [MEDIUM] gomodules: Path Traversal
    [MEDIUM] gomodules: Path Traversal
    [MEDIUM] gomodules: Path Traversal
    [MEDIUM] gomodules: Path Traversal
    [MEDIUM] gomodules: Path Traversal
    [MEDIUM] gomodules: Path Traversal
    [MEDIUM] gomodules: Path Traversal
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Uncontrolled Recursion
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Uncontrolled Recursion
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Uncontrolled Recursion
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Uncontrolled Recursion
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Uncontrolled Recursion
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Uncontrolled Recursion
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Uncontrolled Recursion
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Uncontrolled Recursion
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Uncontrolled Recursion
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Uncontrolled Recursion
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Uncontrolled Recursion
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Uncontrolled Recursion
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Uncontrolled Recursion
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Uncontrolled Recursion
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Use of Uninitialized Resource
    [MEDIUM] gomodules: NULL Pointer Dereference
    [MEDIUM] gomodules: Path Traversal
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Use of Uninitialized Resource
    [MEDIUM] gomodules: NULL Pointer Dereference
    [MEDIUM] gomodules: Path Traversal
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Use of Uninitialized Resource
    [MEDIUM] gomodules: NULL Pointer Dereference
    [MEDIUM] gomodules: Path Traversal
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Use of Uninitialized Resource
    [MEDIUM] gomodules: NULL Pointer Dereference
    [MEDIUM] gomodules: Path Traversal
    [HIGH] gomodules: Allocation of Resources Without Limits or Throttling
    [HIGH] gomodules: Use of Uninitialized Resource
    [MEDIUM] gomodules: NULL Pointer Dereference
    [MEDIUM] gomodules: Path Traversal
    [HIGH] gomodules: Arbitrary Code Injection
    [MEDIUM] gomodules: Path Traversal
    [MEDIUM] gomodules: Information Exposure
    [MEDIUM] gomodules: Information Exposure
    [HIGH] gomodules: Use of Uninitialized Resource
    [MEDIUM] gomodules: Path Traversal
    [HIGH] gomodules: Use of Uninitialized Resource
    [HIGH] gomodules: Use of Uninitialized Resource
    [HIGH] gomodules: Use of Uninitialized Resource
    [HIGH] gomodules: Use of Uninitialized Resource
    [MEDIUM] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Use of Uninitialized Resource
    [HIGH] gomodules: Use of Uninitialized Resource
    [MEDIUM] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Use of Uninitialized Resource
    [HIGH] gomodules: Use of Uninitialized Resource
    [MEDIUM] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Use of Uninitialized Resource
    [HIGH] gomodules: Use of Uninitialized Resource
    [MEDIUM] gomodules: NULL Pointer Dereference
    [HIGH] gomodules: Use of Uninitialized Resource
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
    [HIGH] gomodules: Denial of Service (DoS)
"""

def extract_high_critical(text):
    lines = text.strip().splitlines()
    unique_vulns = set()

    for line in lines:
        line = line.strip()
        if line.startswith("[HIGH]") or line.startswith("[CRITICAL]"):
            unique_vulns.add(line)

    with open("high_critical.txt", "w") as f:
        f.write("Unique HIGH and CRITICAL Vulnerabilities:\n\n")
        for vuln in sorted(unique_vulns):
            f.write(vuln + "\n")

    print(f"Extracted {len(unique_vulns)} unique HIGH/CRITICAL vulnerabilities.")
    print("Results saved in high_critical.txt")


if __name__ == "__main__":
    extract_high_critical(raw_text)
