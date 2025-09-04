import React, { useState } from 'react';
import { Button, Heading } from '@radix-ui/themes';
import { FEATURE_ORDER, mockApiUpdatePermissionByUserId, type FeatureRow } from '../ListPermissionUser/tableConfig';
import PermissionUserForm from '../FormPermissionUser';

export default function CreatePermissionUser() {
  const [data, setData] = useState<FeatureRow[]>(
    FEATURE_ORDER.map((feature) => ({
      feature,
      name: feature.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase()), // optional: format "api_doc" -> "Api Doc"
      read: false,
      write: false,
    }))
  );

  const handleSubmit = () => {
    const newUserId = 'new-user-id'; // replace with real logic
    mockApiUpdatePermissionByUserId(newUserId, data).then(() => {
      alert('Created successfully!');
    });
  };

  return (
    <div>
      <Heading size="5" mb="4">
        Create New User Permission
      </Heading>

      <PermissionUserForm data={data} onChange={setData} />

      <Button onClick={handleSubmit} mt="4">
        Create
      </Button>
    </div>
  );
}
