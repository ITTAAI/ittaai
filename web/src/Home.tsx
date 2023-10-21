import {
    Box,
    Button,
    CircularProgress,
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
import {useRecoilValue} from "recoil";
import {captionState} from "./states/captionState.ts";
import {useEffect, useRef, useState} from "react";
import axios from "axios";
import useSWR from "swr";

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
    // @ts-ignore
    const fetcher = (...args: any[]) => fetch(...args).then((res) => res.json())
    const caption = useRecoilValue(captionState)
    const [value, setValue] = useState('')
    const [gptResult, setGptResult] = useState('')
    const [loading, setLoading] = useState(false)
    const scrollContainerRef = useRef<any>(null);
    const gptResultController = useRef<any>(null)

    const {data, error, isLoading} = useSWR("http://127.0.0.1:8000/get_summary", fetcher, {
        refreshInterval: 1000,
    })

    console.log(error, isLoading, data)

    useEffect(() => {
        if (scrollContainerRef.current) {
            const container = scrollContainerRef.current;
            container.scrollTop = container.scrollHeight;
        }
    }, [caption.value]);


    useEffect(() => {
        if (gptResultController.current) {
            const container = gptResultController.current;
            container.scrollTop = container.scrollHeight;
        }
    }, [gptResult]);

    const onSend = async () => {
        setLoading(true)

        try {
            const res = await axios.post('http://localhost:8000/submit-form', {
                service: "gpt",
                q: value
            })

            setLoading(false)
            setValue('')
            setGptResult((prevState) => prevState + res.data.data + '\n -- \n')
        } catch (e) {
            setLoading(false)

        }
    }

    return (
        <Grid2 container>
            <Grid2 xs={12}
                   md={6}
                   sx={{
                       p: 5,
                       height: '80vh',
                   }}>
                <div>
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

                        <Paper
                            ref={scrollContainerRef}
                            sx={{
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
                                              value={caption.value}
                            />
                        </Paper>
                        <Audio/>
                    </Stack>
                </div>

                <Box sx={{
                    mt: 2
                }}>
                    <Divider sx={{
                        mb: 2
                    }}/>
                    <Button variant={"outlined"}
                            color={'secondary'}>
                        AI Summary
                    </Button>

                    <TextareaAutosize value={data?.summary}
                                      minRows={3}
                                      disabled
                                      sx={{
                                          width: '95%',
                                          border: 'none',
                                      }}/>
                </Box>
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
                            Ask AI
                        </Button>
                    </Box>

                    <Divider/>

                    <Paper
                        ref={gptResultController}
                        sx={{
                            height: '100%',
                            display: 'grid',
                            direction: 'column',
                            bgcolor: 'transparent',
                        }}>

                        <TextareaAutosize minRows={10}
                                          disabled
                                          sx={{
                                              width: '95%',
                                              border: 'none',
                                              bgcolor: 'transparent',
                                          }}
                                          value={gptResult}
                        />
                    </Paper>
                    <OutlinedInput
                        value={value}
                        onChange={(e) => setValue(e.target.value)}
                        endAdornment={<InputAdornment position="end">
                            {!loading ?
                                <IconButton onClick={onSend}
                                            onKeyPress={onSend}>
                                    <SendOutlined/>
                                </IconButton>
                                :
                                <CircularProgress/>
                            }
                        </InputAdornment>}
                        sx={{
                            width: '100%',
                        }}/>
                </Stack>
            </Grid2>
        </Grid2>
    );
}

export default Home;