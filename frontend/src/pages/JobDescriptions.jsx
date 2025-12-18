import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Button,
  Box,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Delete as DeleteIcon,
  Business as BusinessIcon,
  LocationOn as LocationIcon,
  Work as WorkIcon,
  Visibility as ViewIcon
} from '@mui/icons-material';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { API_BASE_URL } from '../config/firebase';
import { toast } from 'react-toastify';
import { motion } from 'framer-motion';

const JobDescriptions = () => {
  const { token } = useAuth();
  const [jds, setJds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [deleteDialog, setDeleteDialog] = useState({ open: false, id: null });

  useEffect(() => {
    fetchJDs();
  }, []);

  const fetchJDs = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/jds/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setJds(response.data);
    } catch (error) {
      console.error('Failed to fetch job descriptions:', error);
      toast.error('Failed to fetch job descriptions');
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (event) => {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

    setUploading(true);
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));

    try {
      const response = await axios.post(`${API_BASE_URL}/api/jds/upload`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      toast.success(`Successfully uploaded ${response.data.length} JD(s) and matched candidates`);
      fetchJDs();
    } catch (error) {
      console.error('Upload error:', error);
      toast.error(error.response?.data?.detail || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
      event.target.value = null;
    }
  };

  const handleDelete = async () => {
    try {
      await axios.delete(`${API_BASE_URL}/api/jds/${deleteDialog.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Job description deleted successfully');
      fetchJDs();
    } catch (error) {
      toast.error('Failed to delete job description');
    }
    setDeleteDialog({ open: false, id: null });
  };

  const handleViewJD = async (jdId) => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/jds/download/${jdId}`,
        {
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob'
        }
      );
      
      const blob = new Blob([response.data], { type: response.headers['content-type'] });
      const blobUrl = window.URL.createObjectURL(blob);
      window.open(blobUrl, '_blank');
      
      setTimeout(() => window.URL.revokeObjectURL(blobUrl), 100);
    } catch (error) {
      console.error('Failed to open JD file:', error);
      toast.error('Failed to open JD file');
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
      >
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
          <Box>
            <Typography variant="h4" fontWeight="bold" gutterBottom>
              📋 Job Descriptions
            </Typography>
            <Typography color="text.secondary">
              {jds.length} job description{jds.length !== 1 ? 's' : ''} active
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={uploading ? <CircularProgress size={20} /> : <UploadIcon />}
            component="label"
            disabled={uploading}
            sx={{
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: 4,
              }
            }}
          >
            {uploading ? 'Uploading...' : 'Upload JDs'}
            <input
              type="file"
              hidden
              multiple
              accept=".pdf,.docx"
              onChange={handleUpload}
            />
          </Button>
        </Box>
      </motion.div>

      {/* JDs Grid */}
      {jds.length === 0 ? (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 8 }}>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No job descriptions yet
              </Typography>
              <Typography color="text.secondary" paragraph>
                Upload JDs to automatically match with candidates
              </Typography>
              <Button variant="contained" startIcon={<UploadIcon />} component="label">
                Upload First JD
                <input type="file" hidden multiple accept=".pdf,.docx" onChange={handleUpload} />
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      ) : (
        <Grid container spacing={3}>
          {jds.map((jd, index) => (
            <Grid item xs={12} md={6} lg={4} key={jd.jd_id}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ 
                  duration: 0.4, 
                  delay: index * 0.05,
                  ease: [0.4, 0, 0.2, 1]
                }}
              >
                <Card
                  sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    '&:hover': {
                      boxShadow: 6,
                      transform: 'translateY(-4px)'
                    }
                  }}
                >
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="start" mb={2}>
                      <Box>
                        <Typography variant="h6" fontWeight="600">
                          {jd.job_title}
                        </Typography>
                        {jd.company && (
                          <Typography variant="body2" color="text.secondary">
                            {jd.company}
                          </Typography>
                        )}
                      </Box>
                      <Box display="flex" gap={1}>
                        <IconButton
                          size="small"
                          color="primary"
                          onClick={() => handleViewJD(jd.jd_id)}
                          title="View Job Description"
                        >
                          <ViewIcon />
                        </IconButton>
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => setDeleteDialog({ open: true, id: jd.jd_id })}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                    </Box>

                    <Box display="flex" flexDirection="column" gap={1} mb={2}>
                      {jd.location && (
                        <Box display="flex" alignItems="center" gap={1}>
                          <LocationIcon fontSize="small" color="action" />
                          <Typography variant="body2">{jd.location}</Typography>
                        </Box>
                      )}
                      {jd.job_type && (
                        <Box display="flex" alignItems="center" gap={1}>
                          <WorkIcon fontSize="small" color="action" />
                          <Typography variant="body2">{jd.job_type}</Typography>
                        </Box>
                      )}
                      {jd.experience_required && (
                        <Box display="flex" alignItems="center" gap={1}>
                          <BusinessIcon fontSize="small" color="action" />
                          <Typography variant="body2">Exp: {jd.experience_required}</Typography>
                        </Box>
                      )}
                    </Box>

                    {jd.required_skills && jd.required_skills.length > 0 && (
                      <Box>
                        <Typography variant="caption" color="text.secondary" display="block" mb={1}>
                          Required Skills:
                        </Typography>
                        <Box display="flex" flexWrap="wrap" gap={0.5}>
                          {jd.required_skills.slice(0, 5).map((skill, idx) => (
                            <Chip
                              key={idx}
                              label={skill}
                              size="small"
                              color="primary"
                              sx={{ fontSize: '0.75rem' }}
                            />
                          ))}
                          {jd.required_skills.length > 5 && (
                            <Chip
                              label={`+${jd.required_skills.length - 5}`}
                              size="small"
                              variant="outlined"
                              sx={{ fontSize: '0.75rem' }}
                            />
                          )}
                        </Box>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialog.open} onClose={() => setDeleteDialog({ open: false, id: null })}>
        <DialogTitle>Delete Job Description?</DialogTitle>
        <DialogContent>
          <Typography>
            This action cannot be undone. All candidate matches for this JD will also be removed.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog({ open: false, id: null })}>Cancel</Button>
          <Button onClick={handleDelete} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default JobDescriptions;
