import React from 'react';
import { Box } from '@mui/material';

const AppLogo = ({ size = 32, sx = {} }) => (
  <Box
    component="img"
    src="/proxywake.png"
    alt="ProxyWake"
    sx={{
      width: size,
      height: size,
      borderRadius: 2,
      objectFit: 'cover',
      ...sx,
    }}
  />
);

export default AppLogo;
