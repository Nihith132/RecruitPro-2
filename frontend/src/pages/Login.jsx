import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Button, Container, Typography, Card, CardContent } from '@mui/material';
import { Google as GoogleIcon } from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import { toast } from 'react-toastify';

const Login = () => {
  const { signInWithGoogle, user } = useAuth();
  const navigate = useNavigate();

  React.useEffect(() => {
    if (user) {
      navigate('/dashboard');
    }
  }, [user, navigate]);

  const handleGoogleSignIn = async () => {
    try {
      await signInWithGoogle();
      toast.success('Welcome to RecruitPro!');
      navigate('/dashboard');
    } catch (error) {
      toast.error('Failed to sign in. Please try again.');
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Container maxWidth="sm">
        <Card sx={{ borderRadius: 4 }}>
          <CardContent sx={{ p: 6, textAlign: 'center' }}>
            <Box
              sx={{
                width: 80,
                height: 80,
                borderRadius: 3,
                bgcolor: 'primary.main',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontWeight: 'bold',
                fontSize: 40,
                mx: 'auto',
                mb: 3,
              }}
            >
              R
            </Box>

            <Typography variant="h4" fontWeight="bold" gutterBottom>
              RecruitPro 2
            </Typography>

            <Typography variant="body1" color="text.secondary" paragraph>
              AI-powered recruitment management system
            </Typography>

            <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
              Upload resumes, match candidates with job descriptions, and find the perfect fit using advanced AI.
            </Typography>

            <Button
              variant="contained"
              size="large"
              fullWidth
              startIcon={<GoogleIcon />}
              onClick={handleGoogleSignIn}
              sx={{
                py: 1.5,
                fontSize: '1.1rem',
                textTransform: 'none',
                fontWeight: 600,
              }}
            >
              Sign in with Google
            </Button>

            <Typography variant="caption" color="text.secondary" sx={{ mt: 3, display: 'block' }}>
              By signing in, you agree to our Terms of Service and Privacy Policy
            </Typography>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
};

export default Login;
