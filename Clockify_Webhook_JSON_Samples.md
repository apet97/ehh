# Clockify Webhook JSON Response Samples

## APPROVAL_REQUEST_STATUS_UPDATED
```json
{
    "id": "61c9b4666574753612c708f4",
    "workspaceId": "613871c9050bf21482aad3a2",
    "dateRange": {
        "start": "2021-12-18T23:00:00Z",
        "end": "2021-12-25T22:59:59Z"
    },
    "owner": {
        "userId": "6137bb5addd64b2759e031e7",
        "userName": "John Doe",
        "timezone": "Europe/Berlin",
        "startOfWeek": "SUNDAY"
    },
    "status": {
        "state": "PENDING",
        "updatedBy": "6137bb5addd64b2759e031e7",
        "updatedByUserName": "Filip Petrovic",
        "updatedAt": "2021-12-27T12:41:00Z",
        "note": ""
    }
}
```

## ASSIGNMENT_CREATED
```json
{
    "workspaceId": "6137bb5addd64b2759e031e8",
    "userId": "61387478050bf21482aad3a8",
    "projectId": "658422d9ac7a9530e4f049ea",
    "assignmentId": "658e6c507c6dd067d908c8f5"
}
```

## ASSIGNMENT_DELETED
```json
{
    "workspaceId": "6137bb5addd64b2759e031e8",
    "userId": "61387478050bf21482aad3a8",
    "projectId": "658422d9ac7a9530e4f049ea",
    "assignmentId": "658e6c507c6dd067d908c8f5"
}
```

## ASSIGNMENT_PUBLISHED
```json
{
    "workspaceId": "6137bb5addd64b2759e031e8",
    "userId": "61387478050bf21482aad3a8",
    "projectId": "658422d9ac7a9530e4f049ea",
    "assignmentId": "658e6c507c6dd067d908c8f5"
}
```

## ASSIGNMENT_UPDATED
```json
{
    "workspaceId": "6137bb5addd64b2759e031e8",
    "userId": "61387478050bf21482aad3a8",
    "projectId": "658422d9ac7a9530e4f049ea",
    "assignmentId": "658e6c507c6dd067d908c8f5"
}
```

## BALANCE_UPDATED
```json
{
    "workspaceId": "6137bb5addd64b2759e031e8",
    "userId": "61387478050bf21482aad3a8",
    "value": "10",
    "note": "Overtime",
    "updatedBy": "6137bb5addd64b2759e031e7"
}
```

## BILLABLE_RATE_UPDATED
```json
{
    "workspaceId": "5f11791a4e759e12c40733ba",
    "rateChangeSource": "PROJECT_MEMBER",
    "modifiedEntity": {
        "userId": "5bfd36c4b0798777049512e2",
        "hourlyRate": {
            "amount": 150
        },
        "costRate": {
            "amount": 0
        },
        "targetId": "5f1185197db7a8637ffcaf1d",
        "membershipType": "PROJECT",
        "membershipStatus": "ACTIVE"
    },
    "currency": {
        "id": "6491a2bc553c4727153f4d96",
        "code": "USD"
    },
    "amount": 150,
    "since": "2024-12-18T23:00:00Z"
}
```

## CLIENT_DELETED
```json
{
    "id": "5f118af27db7a8637ffcaf30",
    "name": "Webhook Test Client",
    "workspaceId": "5f11791a4e759e12c40733ba",
    "archived": false
}
```

## CLIENT_UPDATED
```json
{
    "id": "5f118af27db7a8637ffcaf30",
    "name": "Webhook Test Client",
    "workspaceId": "5f11791a4e759e12c40733ba",
    "archived": false
}
```

## COST_RATE_UPDATED
```json
{
    "workspaceId": "5f11791a4e759e12c40733ba",
    "rateChangeSource": "PROJECT_MEMBER",
    "modifiedEntity": {
        "userId": "5bfd36c4b0798777049512e2",
        "hourlyRate": {
            "amount": 0
        },
        "costRate": {
            "amount": 100
        },
        "targetId": "5f1185197db7a8637ffcaf1d",
        "membershipType": "PROJECT",
        "membershipStatus": "ACTIVE"
    },
    "currency": {
        "id": "6491a2bc553c4727153f4d96",
        "code": "USD"
    },
    "amount": 100,
    "since": "2024-12-18T23:00:00Z"
}
```

## EXPENSE_CREATED
```json
{
    "id": "68ae0cafcef78725aa10db15",
    "workspaceId": "68adfddad138cb5f24c63b22",
    "userId": "64621faec4d2cc53b91fce6c",
    "date": "2025-08-26T00:00:00Z",
    "projectId": "68ae0b03dc4864638480887f",
    "taskId": null,
    "categoryId": "68ae0c8189b9b14a1304e26e",
    "notes": "",
    "quantity": 22,
    "billable": true,
    "fileId": "",
    "total": 220000
}
```

## EXPENSE_DELETED
```json
{
    "workspaceId": "6137bb5addd64b2759e031e8",
    "userId": "61387478050bf21482aad3a8",
    "projectId": "658422d9ac7a9530e4f049ea",
    "expenseId": "658e6c507c6dd067d908c8f5",
    "categoryId": "65842232ac7a9530e4f049df"
}
```

## EXPENSE_RESTORED
```json
{
    "id": "6626722235baad1bce9e13c4",
    "workspaceId": "65f31c3ca1390f6d7cf1d033",
    "userId": "65f31c3ca1390f6d7cf1d032",
    "date": "2024-04-22T00:00:00Z",
    "projectId": "6606d1c0ad0bc15d89f41ae0",
    "categoryId": "660298b663b23a11842833e8",
    "notes": "",
    "quantity": 1,
    "billable": true,
    "fileId": "",
    "total": 500,
    "locked": false
}
```

## EXPENSE_UPDATED
```json
{
    "workspaceId": "6137bb5addd64b2759e031e8",
    "userId": "61387478050bf21482aad3a8",
    "projectId": "658422d9ac7a9530e4f049ea",
    "expenseId": "658e6c507c6dd067d908c8f5",
    "categoryId": "65842232ac7a9530e4f049df"
}
```

## INVOICE_UPDATED
```json
{
    "id": "61b741a6f2147a59acc0918d",
    "number": "Webhook Test Number",
    "status": "UNSENT",
    "issuedDate": "2021-12-23T00:00:00Z",
    "dueDate": "2021-12-23T00:00:00Z",
    "subtotal": 0,
    "discount": 0,
    "tax": 0,
    "tax2": 0,
    "discountAmount": 0,
    "taxAmount": 0,
    "tax2Amount": 0,
    "amount": 0,
    "currency": "USD",
    "subject": "test subject",
    "note": "test note",
    "clientId": "61a912385bee2b729b11f676",
    "clientName": "test client name",
    "clientAddress": "Test client address",
    "userId": "619ccf3569d27064406805d4",
    "items": [
        {
            "order": 1,
            "quantity": 500,
            "description": "test order item description",
            "unitPrice": 500,
            "amount": 2500,
            "itemType": null,
            "timeEntryIds": []
        }
    ]
}
```

## LIMITED_USERS_ADDED_TO_WORKSPACE
```json
{
    "workspaceId": "5f11791a4e759e12c40733ba",
    "inviter": {
        "id": "5bfd36c4b0798777049512e2",
        "email": "email@test.com",
        "name": "Username",
        "profilePicture": "https://img.clockify.me/no-user-image.png"
    },
    "invitedUserNames": [
        "Test Limited User 1",
        "Test Limited User 2",
        "Test Limited User 3"
    ]
}
```

## NEW_APPROVAL_REQUEST
```json
{
    "id": "61c9b4666574753612c708f4",
    "workspaceId": "613871c9050bf21482aad3a2",
    "dateRange": {
        "start": "2021-12-18T23:00:00Z",
        "end": "2021-12-25T22:59:59Z"
    },
    "owner": {
        "userId": "6137bb5addd64b2759e031e7",
        "userName": "John Doe",
        "timezone": "Europe/Berlin",
        "startOfWeek": "SUNDAY"
    },
    "status": {
        "state": "PENDING",
        "updatedBy": "6137bb5addd64b2759e031e7",
        "updatedByUserName": "Filip Petrovic",
        "updatedAt": "2021-12-27T12:41:00Z",
        "note": ""
    }
}
```

## NEW_CLIENT
```json
{
    "id": "5f118af27db7a8637ffcaf30",
    "name": "Webhook Test Client",
    "workspaceId": "5f11791a4e759e12c40733ba",
    "archived": false
}
```

## NEW_INVOICE
```json
{
    "id": "61b741a6f2147a59acc0918d",
    "number": "Webhook Test Number",
    "status": "UNSENT",
    "issuedDate": "2021-12-23T00:00:00Z",
    "dueDate": "2021-12-23T00:00:00Z",
    "subtotal": 0,
    "discount": 0,
    "tax": 0,
    "tax2": 0,
    "discountAmount": 0,
    "taxAmount": 0,
    "tax2Amount": 0,
    "amount": 0,
    "currency": "USD",
    "subject": "test subject",
    "note": "test note",
    "clientId": "61a912385bee2b729b11f676",
    "clientName": "test client name",
    "clientAddress": "Test client address",
    "userId": "619ccf3569d27064406805d4",
    "items": [
        {
            "order": 1,
            "quantity": 500,
            "description": "test order item description",
            "unitPrice": 500,
            "amount": 2500,
            "itemType": null,
            "timeEntryIds": []
        }
    ]
}
```

## NEW_PROJECT
```json
{
    "id": "5f1185197db7a8637ffcaf1d",
    "name": "Webhook Test Project",
    "hourlyRate": {
        "amount": 1000
    },
    "clientId": "5f1183584e759e12c40733cb",
    "workspaceId": "5f11791a4e759e12c40733ba",
    "billable": true,
    "color": "#795548",
    "estimate": {
        "estimate": "PT0S",
        "type": "AUTO"
    },
    "archived": false,
    "duration": "PT0S",
    "clientName": "Client",
    "note": "Test Note",
    "public": true,
    "template": false,
    "tasks": [
        {
            "name": "First task",
            "projectId": "5f1185197db7a8637ffcaf1d",
            "assigneeId": "",
            "assigneeIds": [],
            "userGroupIds": [],
            "estimate": "PT0S",
            "duration": "PT0S",
            "status": "ACTIVE",
            "workspaceId": "5f11791a4e759e12c40733ba",
            "id": "5f1185197db7a8637ffcaf1e"
        }
    ],
    "client": {
        "name": "Client",
        "workspaceId": "5f11791a4e759e12c40733ba",
        "archived": false,
        "id": "5f1183584e759e12c40733cb"
    }
}
```

## NEW_TAG
```json
{
    "id": "5f118b747db7a8637ffcaf33",
    "name": "Webhook Test Tag",
    "workspaceId": "5f11791a4e759e12c40733ba",
    "archived": false
}
```

## NEW_TASK
```json
{
    "id": "5f1189847db7a8637ffcaf25",
    "name": "Webhook Test Task",
    "projectId": "5f11849d4e759e12c40733d5",
    "assigneeIds": [
        "5bf6d2b9b079876a34621635"
    ],
    "assigneeId": "5bf6d2b9b079876a34621635",
    "userGroupIds": [],
    "estimate": "PT0S",
    "status": "ACTIVE",
    "duration": "PT0S"
}
```

## NEW_TIMER_STARTED
```json
{
    "id": "5f118c837db7a8637ffcaf36",
    "description": "Webhook Test Description",
    "tagIds": [
        "5f118b747db7a8637ffcaf33"
    ],
    "userId": "5ef1cf219f130f232cc34ddc",
    "billable": true,
    "taskId": "5f1189847db7a8637ffcaf25",
    "projectId": "5f11849d4e759e12c40733d5",
    "timeInterval": {
        "start": "2020-07-17T11:35:01Z",
        "end": null,
        "duration": null
    },
    "workspaceId": "5f11791a4e759e12c40733ba",
    "isLocked": false,
    "hourlyRate": null,
    "costRate": null,
    "customFieldValues": [
        {
            "customFieldId": "5f118d9a7db7a8637ffcaf47",
            "timeEntryId": "5f118de07db7a8637ffcaf59",
            "value": "Custom field test value",
            "name": "Custom field"
        }
    ],
    "project": {
        "name": "Project",
        "clientId": "5f1183584e759e12c40733cb",
        "clientName": "Client",
        "workspaceId": "5f11791a4e759e12c40733ba",
        "billable": true,
        "estimate": {
            "estimate": "PT0S",
            "type": "AUTO"
        },
        "color": "#795548",
        "archived": false,
        "duration": "PT0S",
        "note": "Test Note",
        "id": "5f11849d4e759e12c40733d5",
        "public": true,
        "template": false
    },
    "task": {
        "name": "Task",
        "workspaceId": "5f11791a4e759e12c40733ba",
        "projectId": "5f11849d4e759e12c40733d5",
        "assigneeIds": [
            "5bf6d2b9b079876a34621635"
        ],
        "assigneeId": "5bf6d2b9b079876a34621635",
        "userGroupIds": [],
        "estimate": "PT0S",
        "status": "ACTIVE",
        "duration": "PT0S",
        "id": "5f1189847db7a8637ffcaf25"
    },
    "user": {
        "name": "User",
        "id": "5ef1cf219f130f232cc34ddc",
        "status": "PENDING_EMAIL_VERIFICATION"
    },
    "tags": [
        {
            "name": "Tag",
            "workspaceId": "5f11791a4e759e12c40733ba",
            "archived": false,
            "id": "5f118b747db7a8637ffcaf33"
        }
    ]
}
```

## NEW_TIME_ENTRY
```json
{
    "id": "5f118c837db7a8637ffcaf36",
    "description": "Webhook Test Description",
    "tagIds": [
        "5f118b747db7a8637ffcaf33"
    ],
    "userId": "5ef1cf219f130f232cc34ddc",
    "billable": true,
    "taskId": "5f1189847db7a8637ffcaf25",
    "projectId": "5f11849d4e759e12c40733d5",
    "timeInterval": {
        "start": "2020-07-17T11:35:01Z",
        "end": "2020-07-17T12:35:01Z",
        "duration": "PT1H"
    },
    "workspaceId": "5f11791a4e759e12c40733ba",
    "isLocked": false,
    "hourlyRate": null,
    "costRate": null,
    "customFieldValues": [
        {
            "customFieldId": "5f118d9a7db7a8637ffcaf47",
            "timeEntryId": "5f118de07db7a8637ffcaf59",
            "value": "Custom field test value",
            "name": "Custom field"
        }
    ],
    "project": {
        "name": "Project",
        "clientId": "5f1183584e759e12c40733cb",
        "clientName": "Client",
        "workspaceId": "5f11791a4e759e12c40733ba",
        "billable": true,
        "estimate": {
            "estimate": "PT0S",
            "type": "AUTO"
        },
        "color": "#795548",
        "archived": false,
        "duration": "PT0S",
        "note": "Test Note",
        "id": "5f11849d4e759e12c40733d5",
        "public": true,
        "template": false
    },
    "task": {
        "name": "Task",
        "workspaceId": "5f11791a4e759e12c40733ba",
        "projectId": "5f11849d4e759e12c40733d5",
        "assigneeIds": [
            "5bf6d2b9b079876a34621635"
        ],
        "assigneeId": "5bf6d2b9b079876a34621635",
        "userGroupIds": [],
        "estimate": "PT0S",
        "status": "ACTIVE",
        "duration": "PT0S",
        "id": "5f1189847db7a8637ffcaf25"
    },
    "user": {
        "name": "User",
        "id": "5ef1cf219f130f232cc34ddc",
        "status": "PENDING_EMAIL_VERIFICATION"
    },
    "tags": [
        {
            "name": "Tag",
            "workspaceId": "5f11791a4e759e12c40733ba",
            "archived": false,
            "id": "5f118b747db7a8637ffcaf33"
        }
    ]
}
```

## PROJECT_DELETED
```json
{
    "id": "5f1185197db7a8637ffcaf1d",
    "name": "Webhook Test Project",
    "hourlyRate": {
        "amount": 1000
    },
    "clientId": "5f1183584e759e12c40733cb",
    "workspaceId": "5f11791a4e759e12c40733ba",
    "billable": true,
    "color": "#795548",
    "estimate": {
        "estimate": "PT0S",
        "type": "AUTO"
    },
    "archived": false,
    "duration": "PT0S",
    "clientName": "Client",
    "note": "Test Note",
    "public": true,
    "template": false,
    "tasks": [
        {
            "name": "First task",
            "projectId": "5f1185197db7a8637ffcaf1d",
            "assigneeId": "",
            "assigneeIds": [],
            "userGroupIds": [],
            "estimate": "PT0S",
            "duration": "PT0S",
            "status": "ACTIVE",
            "workspaceId": "5f11791a4e759e12c40733ba",
            "id": "5f1185197db7a8637ffcaf1e"
        }
    ],
    "client": {
        "name": "Client",
        "workspaceId": "5f11791a4e759e12c40733ba",
        "archived": false,
        "id": "5f1183584e759e12c40733cb"
    }
}
```

## PROJECT_UPDATED
```json
{
    "id": "5f1185197db7a8637ffcaf1d",
    "name": "Webhook Test Project",
    "hourlyRate": {
        "amount": 1000
    },
    "clientId": "5f1183584e759e12c40733cb",
    "workspaceId": "5f11791a4e759e12c40733ba",
    "billable": true,
    "color": "#795548",
    "estimate": {
        "estimate": "PT0S",
        "type": "AUTO"
    },
    "archived": false,
    "duration": "PT0S",
    "clientName": "Client",
    "note": "Test Note",
    "public": true,
    "template": false,
    "tasks": [
        {
            "name": "First task",
            "projectId": "5f1185197db7a8637ffcaf1d",
            "assigneeId": "",
            "assigneeIds": [],
            "userGroupIds": [],
            "estimate": "PT0S",
            "duration": "PT0S",
            "status": "ACTIVE",
            "workspaceId": "5f11791a4e759e12c40733ba",
            "id": "5f1185197db7a8637ffcaf1e"
        }
    ],
    "client": {
        "name": "Client",
        "workspaceId": "5f11791a4e759e12c40733ba",
        "archived": false,
        "id": "5f1183584e759e12c40733cb"
    }
}
```

## TAG_DELETED
```json
{
    "id": "5f118b747db7a8637ffcaf33",
    "name": "Webhook Test Tag",
    "workspaceId": "5f11791a4e759e12c40733ba",
    "archived": false
}
```

## TAG_UPDATED
```json
{
    "id": "5f118b747db7a8637ffcaf33",
    "name": "Webhook Test Tag",
    "workspaceId": "5f11791a4e759e12c40733ba",
    "archived": false
}
```

## TASK_DELETED
```json
{
    "id": "5f1189847db7a8637ffcaf25",
    "name": "Webhook Test Task",
    "projectId": "5f11849d4e759e12c40733d5",
    "assigneeIds": [
        "5bf6d2b9b079876a34621635"
    ],
    "assigneeId": "5bf6d2b9b079876a34621635",
    "userGroupIds": [],
    "estimate": "PT0S",
    "status": "ACTIVE",
    "duration": "PT0S"
}
```

## TASK_UPDATED
```json
{
    "id": "5f1189847db7a8637ffcaf25",
    "name": "Webhook Test Task",
    "projectId": "5f11849d4e759e12c40733d5",
    "assigneeIds": [
        "5bf6d2b9b079876a34621635"
    ],
    "assigneeId": "5bf6d2b9b079876a34621635",
    "userGroupIds": [],
    "estimate": "PT0S",
    "status": "ACTIVE",
    "duration": "PT0S"
}
```

## TIMER_STOPPED
```json
{
    "id": "5f118c837db7a8637ffcaf36",
    "description": "Webhook Test Description",
    "tagIds": [
        "5f118b747db7a8637ffcaf33"
    ],
    "userId": "5ef1cf219f130f232cc34ddc",
    "billable": true,
    "taskId": "5f1189847db7a8637ffcaf25",
    "projectId": "5f11849d4e759e12c40733d5",
    "timeInterval": {
        "start": "2020-07-17T11:35:01Z",
        "end": "2020-07-17T12:35:01Z",
        "duration": "PT1H"
    },
    "workspaceId": "5f11791a4e759e12c40733ba",
    "isLocked": false,
    "hourlyRate": null,
    "costRate": null,
    "customFieldValues": [
        {
            "customFieldId": "5f118d9a7db7a8637ffcaf47",
            "timeEntryId": "5f118de07db7a8637ffcaf59",
            "value": "Custom field test value",
            "name": "Custom field"
        }
    ],
    "project": {
        "name": "Project",
        "clientId": "5f1183584e759e12c40733cb",
        "clientName": "Client",
        "workspaceId": "5f11791a4e759e12c40733ba",
        "billable": true,
        "estimate": {
            "estimate": "PT0S",
            "type": "AUTO"
        },
        "color": "#795548",
        "archived": false,
        "duration": "PT0S",
        "note": "Test Note",
        "id": "5f11849d4e759e12c40733d5",
        "public": true,
        "template": false
    },
    "task": {
        "name": "Task",
        "workspaceId": "5f11791a4e759e12c40733ba",
        "projectId": "5f11849d4e759e12c40733d5",
        "assigneeIds": [
            "5bf6d2b9b079876a34621635"
        ],
        "assigneeId": "5bf6d2b9b079876a34621635",
        "userGroupIds": [],
        "estimate": "PT0S",
        "status": "ACTIVE",
        "duration": "PT0S",
        "id": "5f1189847db7a8637ffcaf25"
    },
    "user": {
        "name": "User",
        "id": "5ef1cf219f130f232cc34ddc",
        "status": "PENDING_EMAIL_VERIFICATION"
    },
    "tags": [
        {
            "name": "Tag",
            "workspaceId": "5f11791a4e759e12c40733ba",
            "archived": false,
            "id": "5f118b747db7a8637ffcaf33"
        }
    ]
}
```

## TIME_ENTRY_BATCH_DELETED
```json
{
  "_note": "skipped by request; no sample provided"
}
```

## TIME_ENTRY_DELETED
```json
{
    "id": "5f118c837db7a8637ffcaf36",
    "description": "Webhook Test Description",
    "tagIds": [
        "5f118b747db7a8637ffcaf33"
    ],
    "userId": "5ef1cf219f130f232cc34ddc",
    "billable": true,
    "taskId": "5f1189847db7a8637ffcaf25",
    "projectId": "5f11849d4e759e12c40733d5",
    "timeInterval": {
        "start": "2020-07-17T11:35:01Z",
        "end": null,
        "duration": null
    },
    "workspaceId": "5f11791a4e759e12c40733ba",
    "isLocked": false,
    "hourlyRate": null,
    "costRate": null,
    "customFieldValues": [
        {
            "customFieldId": "5f118d9a7db7a8637ffcaf47",
            "timeEntryId": "5f118de07db7a8637ffcaf59",
            "value": "Custom field test value",
            "name": "Custom field"
        }
    ],
    "project": {
        "name": "Project",
        "clientId": "5f1183584e759e12c40733cb",
        "clientName": "Client",
        "workspaceId": "5f11791a4e759e12c40733ba",
        "billable": true,
        "estimate": {
            "estimate": "PT0S",
            "type": "AUTO"
        },
        "color": "#795548",
        "archived": false,
        "duration": "PT0S",
        "note": "Test Note",
        "id": "5f11849d4e759e12c40733d5",
        "public": true,
        "template": false
    },
    "task": {
        "name": "Task",
        "workspaceId": "5f11791a4e759e12c40733ba",
        "projectId": "5f11849d4e759e12c40733d5",
        "assigneeIds": [
            "5bf6d2b9b079876a34621635"
        ],
        "assigneeId": "5bf6d2b9b079876a34621635",
        "userGroupIds": [],
        "estimate": "PT0S",
        "status": "ACTIVE",
        "duration": "PT0S",
        "id": "5f1189847db7a8637ffcaf25"
    },
    "user": {
        "name": "User",
        "id": "5ef1cf219f130f232cc34ddc",
        "status": "PENDING_EMAIL_VERIFICATION"
    },
    "tags": [
        {
            "name": "Tag",
            "workspaceId": "5f11791a4e759e12c40733ba",
            "archived": false,
            "id": "5f118b747db7a8637ffcaf33"
        }
    ]
}
```

## TIME_ENTRY_RESTORED
```json
{
    "id": "5f118c837db7a8637ffcaf36",
    "description": "Webhook Test Description",
    "tagIds": [
        "5f118b747db7a8637ffcaf33"
    ],
    "userId": "5ef1cf219f130f232cc34ddc",
    "billable": true,
    "taskId": "5f1189847db7a8637ffcaf25",
    "projectId": "5f11849d4e759e12c40733d5",
    "timeInterval": {
        "start": "2020-07-17T11:35:01Z",
        "end": "2020-07-17T12:35:01Z",
        "duration": "PT1H"
    },
    "workspaceId": "5f11791a4e759e12c40733ba",
    "isLocked": false,
    "hourlyRate": null,
    "costRate": null,
    "customFieldValues": [
        {
            "customFieldId": "5f118d9a7db7a8637ffcaf47",
            "timeEntryId": "5f118de07db7a8637ffcaf59",
            "value": "Custom field test value",
            "name": "Custom field"
        }
    ],
    "project": {
        "name": "Project",
        "clientId": "5f1183584e759e12c40733cb",
        "clientName": "Client",
        "workspaceId": "5f11791a4e759e12c40733ba",
        "billable": true,
        "estimate": {
            "estimate": "PT0S",
            "type": "AUTO"
        },
        "color": "#795548",
        "archived": false,
        "duration": "PT0S",
        "note": "Test Note",
        "id": "5f11849d4e759e12c40733d5",
        "public": true,
        "template": false
    },
    "task": {
        "name": "Task",
        "workspaceId": "5f11791a4e759e12c40733ba",
        "projectId": "5f11849d4e759e12c40733d5",
        "assigneeIds": [
            "5bf6d2b9b079876a34621635"
        ],
        "assigneeId": "5bf6d2b9b079876a34621635",
        "userGroupIds": [],
        "estimate": "PT0S",
        "status": "ACTIVE",
        "duration": "PT0S",
        "id": "5f1189847db7a8637ffcaf25"
    },
    "user": {
        "name": "User",
        "id": "5ef1cf219f130f232cc34ddc",
        "status": "PENDING_EMAIL_VERIFICATION"
    },
    "tags": [
        {
            "name": "Tag",
            "workspaceId": "5f11791a4e759e12c40733ba",
            "archived": false,
            "id": "5f118b747db7a8637ffcaf33"
        }
    ]
}
```

## TIME_ENTRY_SPLIT
```json
{
    "id": "5f118c837db7a8637ffcaf36",
    "description": "Webhook Test Description",
    "tagIds": [
        "5f118b747db7a8637ffcaf33"
    ],
    "userId": "5ef1cf219f130f232cc34ddc",
    "billable": true,
    "taskId": "5f1189847db7a8637ffcaf25",
    "projectId": "5f11849d4e759e12c40733d5",
    "timeInterval": {
        "start": "2020-07-17T11:35:01Z",
        "end": null,
        "duration": null
    },
    "workspaceId": "5f11791a4e759e12c40733ba",
    "isLocked": false,
    "hourlyRate": null,
    "costRate": null,
    "customFieldValues": [
        {
            "customFieldId": "5f118d9a7db7a8637ffcaf47",
            "timeEntryId": "5f118de07db7a8637ffcaf59",
            "value": "Custom field test value",
            "name": "Custom field"
        }
    ],
    "project": {
        "name": "Project",
        "clientId": "5f1183584e759e12c40733cb",
        "clientName": "Client",
        "workspaceId": "5f11791a4e759e12c40733ba",
        "billable": true,
        "estimate": {
            "estimate": "PT0S",
            "type": "AUTO"
        },
        "color": "#795548",
        "archived": false,
        "duration": "PT0S",
        "note": "Test Note",
        "id": "5f11849d4e759e12c40733d5",
        "public": true,
        "template": false
    },
    "task": {
        "name": "Task",
        "workspaceId": "5f11791a4e759e12c40733ba",
        "projectId": "5f11849d4e759e12c40733d5",
        "assigneeIds": [
            "5bf6d2b9b079876a34621635"
        ],
        "assigneeId": "5bf6d2b9b079876a34621635",
        "userGroupIds": [],
        "estimate": "PT0S",
        "status": "ACTIVE",
        "duration": "PT0S",
        "id": "5f1189847db7a8637ffcaf25"
    },
    "user": {
        "name": "User",
        "id": "5ef1cf219f130f232cc34ddc",
        "status": "PENDING_EMAIL_VERIFICATION"
    },
    "tags": [
        {
            "name": "Tag",
            "workspaceId": "5f11791a4e759e12c40733ba",
            "archived": false,
            "id": "5f118b747db7a8637ffcaf33"
        }
    ]
}
```

## TIME_ENTRY_UPDATED
```json
{
    "id": "5f118c837db7a8637ffcaf36",
    "description": "Webhook Test Description",
    "tagIds": [
        "5f118b747db7a8637ffcaf33"
    ],
    "userId": "5ef1cf219f130f232cc34ddc",
    "billable": true,
    "taskId": "5f1189847db7a8637ffcaf25",
    "projectId": "5f11849d4e759e12c40733d5",
    "timeInterval": {
        "start": "2020-07-17T11:35:01Z",
        "end": "2020-07-17T12:35:01Z",
        "duration": "PT1H"
    },
    "workspaceId": "5f11791a4e759e12c40733ba",
    "isLocked": false,
    "hourlyRate": null,
    "costRate": null,
    "customFieldValues": [
        {
            "customFieldId": "5f118d9a7db7a8637ffcaf47",
            "timeEntryId": "5f118de07db7a8637ffcaf59",
            "value": "Custom field test value",
            "name": "Custom field"
        }
    ],
    "project": {
        "name": "Project",
        "clientId": "5f1183584e759e12c40733cb",
        "clientName": "Client",
        "workspaceId": "5f11791a4e759e12c40733ba",
        "billable": true,
        "estimate": {
            "estimate": "PT0S",
            "type": "AUTO"
        },
        "color": "#795548",
        "archived": false,
        "duration": "PT0S",
        "note": "Test Note",
        "id": "5f11849d4e759e12c40733d5",
        "public": true,
        "template": false
    },
    "task": {
        "name": "Task",
        "workspaceId": "5f11791a4e759e12c40733ba",
        "projectId": "5f11849d4e759e12c40733d5",
        "assigneeIds": [
            "5bf6d2b9b079876a34621635"
        ],
        "assigneeId": "5bf6d2b9b079876a34621635",
        "userGroupIds": [],
        "estimate": "PT0S",
        "status": "ACTIVE",
        "duration": "PT0S",
        "id": "5f1189847db7a8637ffcaf25"
    },
    "user": {
        "name": "User",
        "id": "5ef1cf219f130f232cc34ddc",
        "status": "PENDING_EMAIL_VERIFICATION"
    },
    "tags": [
        {
            "name": "Tag",
            "workspaceId": "5f11791a4e759e12c40733ba",
            "archived": false,
            "id": "5f118b747db7a8637ffcaf33"
        }
    ]
}
```

## TIME_OFF_REQUESTED
```json
{
    "id": "630c87ffc2e8b3166121d4fa",
    "userId": "6137bb5addd64b2759e031e7",
    "workspaceId": "6137bb5addd64b2759e031e8",
    "policyId": "6304e59201c5df1a709e145b",
    "timeZone": "Europe/Belgrade",
    "halfDay": false,
    "timeOffPeriod": {
        "period": {
            "start": "2022-08-28T22:00:00Z",
            "end": "2022-08-29T21:59:59.999Z"
        }
    },
    "note": null,
    "status": {
        "statusType": "PENDING",
        "changedByUserId": null,
        "changedByUserName": null,
        "changedAt": null,
        "note": null
    },
    "balanceDiff": 1,
    "createdAt": "2022-08-29T09:33:51.549784Z",
    "requesterUserId": "6137bb5addd64b2759e031e7",
    "excludeDays": [],
    "negativeBalanceUsed": 0,
    "balanceValueAtRequest": 22
}
```

## TIME_OFF_REQUEST_APPROVED
```json
{
    "id": "630c87ffc2e8b3166121d4fa",
    "userId": "6137bb5addd64b2759e031e7",
    "workspaceId": "6137bb5addd64b2759e031e8",
    "policyId": "6304e59201c5df1a709e145b",
    "timeZone": "Europe/Belgrade",
    "halfDay": false,
    "timeOffPeriod": {
        "period": {
            "start": "2022-08-28T22:00:00Z",
            "end": "2022-08-29T21:59:59.999Z"
        }
    },
    "note": null,
    "status": {
        "statusType": "APPROVED",
        "changedByUserId": "68af772a8870291ef0e57292",
        "changedByUserName": "Test username",
        "changedAt": "2025-08-27T21:22:50.562570839Z",
        "note": null
    },
    "balanceDiff": 1,
    "createdAt": "2022-08-29T09:33:51.549784Z",
    "requesterUserId": "6137bb5addd64b2759e031e7",
    "excludeDays": [],
    "negativeBalanceUsed": 0,
    "balanceValueAtRequest": 22
}
```

## TIME_OFF_REQUEST_REJECTED
```json
{
    "id": "630c87ffc2e8b3166121d4fa",
    "userId": "6137bb5addd64b2759e031e7",
    "workspaceId": "6137bb5addd64b2759e031e8",
    "policyId": "6304e59201c5df1a709e145b",
    "timeZone": "Europe/Belgrade",
    "halfDay": false,
    "timeOffPeriod": {
        "period": {
            "start": "2022-08-28T22:00:00Z",
            "end": "2022-08-29T21:59:59.999Z"
        }
    },
    "note": null,
    "status": {
        "statusType": "REJECTED",
        "changedByUserId": "68af77638870291ef0e572d4",
        "changedByUserName": "Test username",
        "changedAt": "2025-08-27T21:23:47.651686319Z",
        "note": "Generic reject note"
    },
    "balanceDiff": 1,
    "createdAt": "2022-08-29T09:33:51.549784Z",
    "requesterUserId": "6137bb5addd64b2759e031e7",
    "excludeDays": [],
    "negativeBalanceUsed": 0,
    "balanceValueAtRequest": 22
}
```

## TIME_OFF_REQUEST_WITHDRAWN
```json
{
    "id": "630c87ffc2e8b3166121d4fa",
    "userId": "6137bb5addd64b2759e031e7",
    "workspaceId": "6137bb5addd64b2759e031e8",
    "policyId": "6304e59201c5df1a709e145b",
    "timeZone": "Europe/Belgrade",
    "halfDay": false,
    "timeOffPeriod": {
        "period": {
            "start": "2022-08-28T22:00:00Z",
            "end": "2022-08-29T21:59:59.999Z"
        }
    },
    "note": null,
    "status": {
        "statusType": "PENDING",
        "changedByUserId": null,
        "changedByUserName": null,
        "changedAt": null,
        "note": null
    },
    "balanceDiff": 1,
    "createdAt": "2022-08-29T09:33:51.549784Z",
    "requesterUserId": "6137bb5addd64b2759e031e7",
    "excludeDays": [],
    "negativeBalanceUsed": 0,
    "balanceValueAtRequest": 22
}
```

## USERS_INVITED_TO_WORKSPACE
```json
{
    "workspaceId": "68adfddad138cb5f24c63b22",
    "inviter": {
        "id": "64621faec4d2cc53b91fce6c",
        "email": "alpettest1@gmail.com",
        "name": "Russ",
        "profilePicture": "https://avatar.cake.com/2025-03-31T14%3A08%3A38.793Zcake-avatar.png",
        "settings": {
            "weekStart": "MONDAY",
            "timeZone": "Europe/Belgrade",
            "timeFormat": "HOUR12",
            "dateFormat": "MM/DD/YYYY",
            "sendNewsletter": false,
            "weeklyUpdates": true,
            "longRunning": true,
            "scheduledReports": false,
            "approval": true,
            "pto": true,
            "alerts": false,
            "reminders": false,
            "onboarding": false,
            "timeTrackingManual": true,
            "summaryReportSettings": {
                "group": "Project",
                "subgroup": "Time Entry"
            },
            "isCompactViewOn": false,
            "dashboardSelection": "TEAM",
            "dashboardViewType": "PROJECT",
            "dashboardPinToTop": false,
            "projectListCollapse": null,
            "collapseAllProjectLists": false,
            "groupSimilarEntriesDisabled": false,
            "myStartOfDay": "16:30",
            "darkTheme": false,
            "projectPickerSpecialFilter": false,
            "lang": "EN",
            "multiFactorEnabled": false,
            "scheduling": false,
            "showOnlyWorkingDays": false,
            "theme": "DEFAULT"
        }
    },
    "invitedUserEmails": [
        "mka19976@toaik.com"
    ]
}
```

## USER_ACTIVATED_ON_WORKSPACE
```json
{
    "id": "68adff1a0734c8108430b40e",
    "email": "mka19976@toaik.com",
    "name": "mka19976",
    "profilePicture": "",
    "settings": {
        "weekStart": "MONDAY",
        "timeZone": "Europe/Belgrade",
        "timeFormat": "HOUR24",
        "dateFormat": "DD/MM/YYYY",
        "sendNewsletter": false,
        "weeklyUpdates": false,
        "longRunning": false,
        "scheduledReports": true,
        "approval": true,
        "pto": true,
        "alerts": true,
        "reminders": true,
        "onboarding": true,
        "timeTrackingManual": false,
        "summaryReportSettings": {
            "group": "Project",
            "subgroup": "Time Entry"
        },
        "isCompactViewOn": false,
        "dashboardSelection": "ME",
        "dashboardViewType": "PROJECT",
        "dashboardPinToTop": false,
        "projectListCollapse": 50,
        "collapseAllProjectLists": false,
        "groupSimilarEntriesDisabled": false,
        "myStartOfDay": "09:00",
        "darkTheme": false,
        "projectPickerSpecialFilter": false,
        "lang": "EN",
        "multiFactorEnabled": false,
        "scheduling": true,
        "showOnlyWorkingDays": false,
        "theme": "DEFAULT"
    }
}
```

## USER_DEACTIVATED_ON_WORKSPACE
```json
{
    "id": "68adfede89b9b14a1302d0f2",
    "email": "hasidac525@evoxury.com",
    "name": "hasidac525",
    "profilePicture": "",
    "settings": {
        "weekStart": "MONDAY",
        "timeZone": "Europe/Belgrade",
        "timeFormat": "HOUR24",
        "dateFormat": "DD/MM/YYYY",
        "sendNewsletter": false,
        "weeklyUpdates": false,
        "longRunning": false,
        "scheduledReports": true,
        "approval": true,
        "pto": true,
        "alerts": true,
        "reminders": true,
        "onboarding": true,
        "timeTrackingManual": false,
        "summaryReportSettings": {
            "group": "Project",
            "subgroup": "Time Entry"
        },
        "isCompactViewOn": false,
        "dashboardSelection": "ME",
        "dashboardViewType": "PROJECT",
        "dashboardPinToTop": false,
        "projectListCollapse": 50,
        "collapseAllProjectLists": false,
        "groupSimilarEntriesDisabled": false,
        "myStartOfDay": "09:00",
        "darkTheme": false,
        "projectPickerSpecialFilter": false,
        "lang": "EN",
        "multiFactorEnabled": false,
        "scheduling": true,
        "showOnlyWorkingDays": false,
        "theme": "DEFAULT"
    }
}
```

## USER_DELETED_FROM_WORKSPACE
```json
{
    "id": "5bfd36c4b0798777049512e2",
    "email": "email@test.com",
    "name": "Username"
}
```

## USER_EMAIL_CHANGED
```json
{
    "id": "5bfd36c4b0798777049512e2",
    "email": "email@test.com",
    "name": "Username",
    "oldEmail": "oldemail@example.com"
}
```

## USER_GROUP_CREATED
```json
{
    "id": "68af6ed4d056f356edd8fb87",
    "name": "WH_TEST_20250827T204715Z_16018_UG",
    "workspaceId": "68adfddad138cb5f24c63b22",
    "userIds": [],
    "teamManagers": []
}
```

## USER_GROUP_DELETED
```json
{
    "id": "68af6f02a3b40d58316d445e",
    "name": "WH_TEST_20250827T204759Z_15477_UG_UPD",
    "workspaceId": "68adfddad138cb5f24c63b22",
    "userIds": [],
    "teamManagers": []
}
```

## USER_GROUP_UPDATED
```json
{
    "id": "68ae0b0482fc591a26b2dbd8",
    "name": "WH_TEST_20250826T192906Z_3649_UG_UPD",
    "workspaceId": "68adfddad138cb5f24c63b22",
    "userIds": [],
    "teamManagers": []
}
```

## USER_JOINED_WORKSPACE
```json
{
    "id": "68adff1a0734c8108430b40e",
    "email": "mka19976@toaik.com",
    "name": "mka19976",
    "profilePicture": "",
    "settings": {
        "weekStart": "MONDAY",
        "timeZone": "Europe/Belgrade",
        "timeFormat": "HOUR24",
        "dateFormat": "DD/MM/YYYY",
        "sendNewsletter": false,
        "weeklyUpdates": false,
        "longRunning": false,
        "scheduledReports": true,
        "approval": true,
        "pto": true,
        "alerts": true,
        "reminders": true,
        "onboarding": true,
        "timeTrackingManual": false,
        "summaryReportSettings": {
            "group": "Project",
            "subgroup": "Time Entry"
        },
        "isCompactViewOn": false,
        "dashboardSelection": "ME",
        "dashboardViewType": "PROJECT",
        "dashboardPinToTop": false,
        "projectListCollapse": 50,
        "collapseAllProjectLists": false,
        "groupSimilarEntriesDisabled": false,
        "myStartOfDay": "09:00",
        "darkTheme": false,
        "projectPickerSpecialFilter": false,
        "lang": "EN",
        "multiFactorEnabled": false,
        "scheduling": true,
        "showOnlyWorkingDays": false,
        "theme": "DEFAULT"
    }
}
```

## USER_UPDATED
```json
{
    "id": "5bfd36c4b0798777049512e2",
    "email": "email@test.com",
    "name": "Username"
}
```