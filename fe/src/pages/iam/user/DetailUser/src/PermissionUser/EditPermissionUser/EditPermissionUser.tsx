import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

import { Button } from '@radix-ui/themes';
import { buildRowsFromMap, mockApiGetPermissionByUserId, mockApiUpdatePermissionByUserId, type FeatureRow } from '../ListPermissionUser/tableConfig';
import PermissionUserForm from '../FormPermissionUser';

export default function EditPermissionUser() {
  const { id = '1' } = useParams();
  const [data, setData] = useState<FeatureRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    mockApiGetPermissionByUserId(id).then((res) => {
      setData(buildRowsFromMap(res));
      setLoading(false);
    });
  }, [id]);

  const handleSubmit = () => {
    mockApiUpdatePermissionByUserId(id, data).then(() => {
      alert('Updated successfully!');
    });
  };

  if (loading) return <div>Loading...</div>;

  return (
    <>
      <PermissionUserForm data={data} onChange={setData} />
      <Button onClick={handleSubmit} style={{ marginTop: 16 }}>
        Save Changes
      </Button>
    </>
  );
}
