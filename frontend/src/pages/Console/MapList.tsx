import React, { useState, useEffect } from 'react';
import { Table, Button, Card, Space, Modal, message, Tooltip, Input, Popconfirm, Upload, Form } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, EyeOutlined, DownloadOutlined } from '@ant-design/icons';
import type { UploadProps, UploadFile } from 'antd';
import { InboxOutlined } from '@ant-design/icons';

const { Dragger } = Upload;

interface MapConfig {
  id: string;
  name: string;
  description?: string;
  filePath: string;
  fileSize: number;
  fileType: string;
  createdAt: string;
  updatedAt: string;
  previewUrl?: string;
}

const MapList: React.FC = () => {
  const [maps, setMaps] = useState<MapConfig[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [isPreviewVisible, setIsPreviewVisible] = useState(false);
  const [currentMap, setCurrentMap] = useState<MapConfig | null>(null);
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [form] = Form.useForm();

  // Mock data for demonstration
  useEffect(() => {
    setLoading(true);
    // In a real application, this would be an API call
    setTimeout(() => {
      const mockData: MapConfig[] = [
        {
          id: '1',
          name: 'Beijing Map',
          description: 'Map of Beijing city center',
          filePath: 'data/beijing_map.pb',
          fileSize: 1024000,
          fileType: 'pb',
          createdAt: '2023-06-01T10:00:00Z',
          updatedAt: '2023-06-02T14:30:00Z',
          previewUrl: 'https://via.placeholder.com/800x600?text=Beijing+Map+Preview'
        },
        {
          id: '2',
          name: 'New York Map',
          description: 'Map of New York city center',
          filePath: 'data/newyork_map.pb',
          fileSize: 1536000,
          fileType: 'pb',
          createdAt: '2023-06-03T09:15:00Z',
          updatedAt: '2023-06-03T09:15:00Z',
          previewUrl: 'https://via.placeholder.com/800x600?text=New+York+Map+Preview'
        }
      ];
      setMaps(mockData);
      setLoading(false);
    }, 1000);
  }, []);

  const handleSearch = (value: string) => {
    setSearchText(value);
  };

  const filteredMaps = maps.filter(map => 
    map.name.toLowerCase().includes(searchText.toLowerCase()) || 
    (map.description && map.description.toLowerCase().includes(searchText.toLowerCase()))
  );

  const handleCreate = () => {
    setCurrentMap(null);
    setFileList([]);
    form.resetFields();
    setIsModalVisible(true);
  };

  const handleEdit = (record: MapConfig) => {
    setCurrentMap(record);
    form.setFieldsValue({
      name: record.name,
      description: record.description
    });
    setIsModalVisible(true);
  };

  const handleDelete = async (id: string) => {
    try {
      setLoading(true);
      // In a real application, this would be an API call
      setTimeout(() => {
        setMaps(maps.filter(map => map.id !== id));
        message.success('Map deleted successfully');
        setLoading(false);
      }, 500);
    } catch {
      message.error('Failed to delete map');
      setLoading(false);
    }
  };

  const handlePreview = (record: MapConfig) => {
    setCurrentMap(record);
    setIsPreviewVisible(true);
  };

  const handleDownload = (record: MapConfig) => {
    // In a real application, this would trigger a file download
    message.success(`Downloading ${record.name}...`);
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);
      
      // In a real application, this would be an API call to save the map
      setTimeout(() => {
        if (currentMap) {
          // Update existing map
          const updatedMaps = maps.map(map => 
            map.id === currentMap.id 
        ? { 
                  ...map, 
            name: values.name,
            description: values.description,
            updatedAt: new Date().toISOString()
          } 
              : map
          );
          setMaps(updatedMaps);
          message.success('Map updated successfully');
        } else if (fileList.length > 0) {
          // Create new map
          const newMap: MapConfig = {
            id: Date.now().toString(),
            name: values.name,
            description: values.description,
            filePath: `data/${values.name.replace(/\s+/g, '_').toLowerCase()}_map.pb`,
            fileSize: fileList[0].size || 1024000,
            fileType: 'pb',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            previewUrl: 'https://via.placeholder.com/800x600?text=New+Map+Preview'
          };
          setMaps([...maps, newMap]);
          message.success('Map uploaded successfully');
        } else {
          message.error('Please upload a map file');
          setLoading(false);
          return;
        }

      setIsModalVisible(false);
      setFileList([]);
      form.resetFields();
        setLoading(false);
      }, 500);
    } catch {
      message.error('Please check the form fields');
      setLoading(false);
    }
  };

  const handleModalCancel = () => {
    setIsModalVisible(false);
    setFileList([]);
    form.resetFields();
  };

  const handlePreviewCancel = () => {
    setIsPreviewVisible(false);
  };

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: false,
    maxCount: 1,
    fileList: fileList,
    beforeUpload: (file) => {
      setFileList([file]);
      return false; // Prevent auto upload
    },
    onRemove: () => {
      setFileList([]);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      sorter: (a: MapConfig, b: MapConfig) => a.name.localeCompare(b.name)
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true
    },
    {
      title: 'File Path',
      dataIndex: 'filePath',
      key: 'filePath'
    },
    {
      title: 'Size',
      dataIndex: 'fileSize',
      key: 'fileSize',
      render: (size: number) => formatFileSize(size),
      sorter: (a: MapConfig, b: MapConfig) => a.fileSize - b.fileSize
    },
    {
      title: 'Last Updated',
      dataIndex: 'updatedAt',
      key: 'updatedAt',
      render: (text: string) => new Date(text).toLocaleString(),
      sorter: (a: MapConfig, b: MapConfig) => 
        new Date(a.updatedAt).getTime() - new Date(b.updatedAt).getTime()
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: unknown, record: MapConfig) => (
        <Space size="small">
          <Tooltip title="Preview">
            <Button 
              icon={<EyeOutlined />} 
              onClick={() => handlePreview(record)} 
              type="text"
            />
          </Tooltip>
          <Tooltip title="Download">
            <Button 
              icon={<DownloadOutlined />} 
              onClick={() => handleDownload(record)} 
              type="text"
            />
          </Tooltip>
          <Tooltip title="Edit">
            <Button 
              icon={<EditOutlined />} 
              onClick={() => handleEdit(record)} 
              type="text"
            />
          </Tooltip>
          <Tooltip title="Delete">
            <Popconfirm
              title="Are you sure you want to delete this map?"
              onConfirm={() => handleDelete(record.id)}
              okText="Yes"
              cancelText="No"
            >
              <Button 
                icon={<DeleteOutlined />} 
                type="text"
                danger
              />
            </Popconfirm>
          </Tooltip>
        </Space>
      )
    }
  ];

  return (
    <Card title="Map Configurations" extra={
      <Space>
        <Input.Search
          placeholder="Search maps"
          onSearch={handleSearch}
          onChange={(e) => handleSearch(e.target.value)}
          style={{ width: 250 }}
        />
        <Button 
          type="primary" 
          icon={<PlusOutlined />} 
          onClick={handleCreate}
        >
          Upload Map
        </Button>
      </Space>
    }>
      <Table 
        columns={columns} 
        dataSource={filteredMaps} 
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10 }}
      />

      <Modal
        title={currentMap ? "Edit Map" : "Upload Map"}
        open={isModalVisible}
        onOk={handleModalOk}
        onCancel={handleModalCancel}
        width={600}
        confirmLoading={loading}
      >
        <Form
          form={form}
          layout="vertical"
        >
          <Form.Item
            name="name"
            label="Map Name"
            rules={[{ required: true, message: 'Please enter map name' }]}
          >
            <Input placeholder="Enter map name" />
          </Form.Item>
          
          <Form.Item
            name="description"
            label="Description"
          >
            <Input.TextArea rows={3} placeholder="Enter map description" />
          </Form.Item>
          
          {!currentMap && (
            <Form.Item
              name="file"
              label="Map File"
              rules={[{ required: true, message: 'Please upload a map file' }]}
            >
              <Dragger {...uploadProps}>
                <p className="ant-upload-drag-icon">
                  <InboxOutlined />
                </p>
                <p className="ant-upload-text">Click or drag file to this area to upload</p>
                <p className="ant-upload-hint">
                  Support for .pb map files
                </p>
              </Dragger>
            </Form.Item>
          )}
        </Form>
      </Modal>

      <Modal
        title={currentMap?.name}
        open={isPreviewVisible}
        onCancel={handlePreviewCancel}
        footer={null}
        width={840}
      >
        {currentMap?.previewUrl && (
          <img 
            src={currentMap.previewUrl} 
            alt={currentMap.name} 
            style={{ width: '100%', height: 'auto' }} 
          />
        )}
      </Modal>
    </Card>
  );
};

export default MapList; 
