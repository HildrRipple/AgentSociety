import React, { useState } from 'react';
import { Form, Input, Card, Upload, Button, message } from 'antd';
import { UploadOutlined, InboxOutlined } from '@ant-design/icons';
import type { UploadProps, UploadFile } from 'antd';
import { MapConfig } from '../../types/config';

const { Dragger } = Upload;

interface MapFormProps {
  value: Partial<MapConfig>;
  onChange: (value: Partial<MapConfig>) => void;
}

const MapForm: React.FC<MapFormProps> = ({ value, onChange }) => {
  const [form] = Form.useForm();
  const [fileList, setFileList] = useState<UploadFile[]>([]);

  // Handle form value changes
  const handleValuesChange = (changedValues: any, allValues: any) => {
    onChange(allValues);
  };

  // Set initial values
  React.useEffect(() => {
    form.setFieldsValue(value);
  }, [form, value]);

  // File upload configuration
  const uploadProps: UploadProps = {
    name: 'file',
    multiple: false,
    fileList,
    beforeUpload: (file) => {
      // Check file type
      const isPbFile = file.name.endsWith('.pb');
      if (!isPbFile) {
        message.error('You can only upload .pb map files!');
        return Upload.LIST_IGNORE;
      }
      
      // Update file list
      setFileList([file]);
      
      // Read file path and update form
      const reader = new FileReader();
      reader.onload = () => {
        // In a real application, this would upload the file to the server
        // and get back a file path. Here we just use the file name.
        const filePath = `./maps/${file.name}`;
        const cachePath = `./maps/cache/${file.name.replace('.pb', '.cache')}`;
        
        form.setFieldsValue({
          file_path: filePath,
          cache_path: cachePath
        });
        
        onChange({
          file_path: filePath,
          cache_path: cachePath
        });
      };
      reader.readAsArrayBuffer(file);
      
      // Prevent default upload behavior
      return false;
    },
    onRemove: () => {
      setFileList([]);
      form.setFieldsValue({
        file_path: '',
        cache_path: ''
      });
      onChange({
        file_path: '',
        cache_path: ''
      });
    },
  };

  return (
    <Form
      form={form}
      layout="vertical"
      onValuesChange={handleValuesChange}
      initialValues={value}
    >
      <Card title="Map File" bordered={false}>
        <Dragger {...uploadProps}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">Click or drag map file to this area to upload</p>
          <p className="ant-upload-hint">
            Support for .pb map files only
          </p>
        </Dragger>
      </Card>

      <Card title="Map Configuration" bordered={false} style={{ marginTop: 16 }}>
        <Form.Item
          name="file_path"
          label="Map File Path"
          rules={[{ required: true, message: 'Please enter map file path' }]}
        >
          <Input placeholder="Enter map file path" />
        </Form.Item>

        <Form.Item
          name="cache_path"
          label="Cache Path"
        >
          <Input placeholder="Enter cache path (optional)" />
        </Form.Item>
      </Card>
    </Form>
  );
};

export default MapForm; 