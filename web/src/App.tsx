import {Box, Divider, ThemeProvider} from "@mui/material";
import {appTheme} from "./theme/app.theme.ts";
import Header from "./components/Header.tsx";
import Home from "./Home.tsx";
import {RecoilRoot} from "recoil";


function App() {

    return (
        <>
            <RecoilRoot>
                <ThemeProvider theme={appTheme}>
                    <Header/>
                    <Divider/>

                    <Box sx={{
                        my: 2,
                        mx: 2
                    }}>
                        <Home></Home>
                    </Box>

                    {/*<Audio/>*/}
                </ThemeProvider>
            </RecoilRoot>
        </>
    )
}

export default App
