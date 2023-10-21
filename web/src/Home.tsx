import {
    Box,
    Button,
    Divider,
    IconButton,
    InputAdornment,
    OutlinedInput,
    Paper,
    Stack,
    styled,
    TextareaAutosize as BaseTextareaAutosize
} from "@mui/material";
import Grid2 from "@mui/material/Unstable_Grid2";
import {SendOutlined} from "@mui/icons-material";
import Audio from "./Audio.tsx";

const blue = {
    100: '#DAECFF',
    200: '#b6daff',
    400: '#3399FF',
    500: '#007FFF',
    600: '#0072E5',
    900: '#003A75',
};

const grey = {
    50: '#f6f8fa',
    100: '#eaeef2',
    200: '#d0d7de',
    300: '#afb8c1',
    400: '#8c959f',
    500: '#6e7781',
    600: '#57606a',
    700: '#424a53',
    800: '#32383f',
    900: '#24292f',
};

const TextareaAutosize = styled(BaseTextareaAutosize)(
    ({theme}) => `
  width: 320px;
  font-family: IBM Plex Sans, sans-serif;
  font-size: 0.875rem;
  font-weight: 400;
  line-height: 1.5;
  padding: 12px;
  border-radius: 12px 12px 0 12px;
  color: ${theme.palette.mode === 'dark' ? grey[300] : grey[900]};
  background: ${theme.palette.mode === 'dark' ? grey[900] : '#fff'};
  // border: 1px solid ${theme.palette.mode === 'dark' ? grey[700] : grey[200]};
  // box-shadow: 0px 2px 24px ${theme.palette.mode === 'dark' ? blue[900] : blue[100]};

  // &:hover {
  //   border-color: ${blue[400]};
  // }
  //
  // &:focus {
  //   border-color: ${blue[400]};
  //   box-shadow: 0 0 0 3px ${theme.palette.mode === 'dark' ? blue[600] : blue[200]};
  // }

  // firefox
  &:focus-visible {
    outline: 0;
  }
`,
);

const Home = () => {
    return (
        <Grid2 container>
            <Grid2 xs={12}
                   md={6}
                   sx={{
                       p: 5,
                       height: '80vh',
                   }}>
                <Stack spacing={2}
                       sx={{
                           height: '100%',
                       }}>
                    <Box sx={{
                        display: 'flex',
                    }}>
                        <Button size={"large"}
                                variant={"contained"}>Detect Audio</Button>
                    </Box>

                    <Divider/>

                    <Paper sx={{
                        height: '100%',
                        display: 'grid',
                        direction: 'column',
                        overflow: 'auto'
                    }}>
                        <TextareaAutosize minRows={10}
                                          disabled
                                          sx={{
                                              width: '95%',
                                              border: 'none',
                                          }}
                                          value={'Hello World'}
                        />
                        <Box sx={{
                            alignSelf: 'end'
                        }}>
                            <Audio/>
                        </Box>
                    </Paper>
                </Stack>
            </Grid2>

            <Grid2 xs={12}
                   md={6}
                   sx={{
                       bgcolor: '#f5f7fc',
                       p: 5,
                       height: '80vh',
                   }}>
                <Stack spacing={2}
                       sx={{
                           height: '100%',
                       }}>
                    <Box sx={{
                        display: 'flex',

                    }}>
                        <Button size={"large"}
                                variant={"contained"}>
                            AI Output
                        </Button>
                    </Box>

                    <Divider/>

                    <Paper sx={{
                        height: '100%',
                        display: 'grid',
                        direction: 'column',
                        bgcolor: 'transparent',
                    }}>

                        <Box sx={{
                            alignSelf: 'end',
                            width: '100%',
                        }}>
                            <OutlinedInput
                                endAdornment={<InputAdornment position="end">
                                    <IconButton>
                                        <SendOutlined/>
                                    </IconButton>
                                </InputAdornment>}
                                sx={{
                                    width: '100%',
                                }}/>
                        </Box>
                    </Paper>
                </Stack>
            </Grid2>
        </Grid2>
    );
}

export default Home;