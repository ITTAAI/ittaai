import {AppBar, Stack, Toolbar, Typography} from "@mui/material";

const Header = () => {
    return (
        <AppBar
            position="static"
            sx={{
                boxShadow: 'none',
                bgcolor: 'white',
                color: 'black',
            }}>
            <Toolbar>
                <Stack direction={"row"}
                       spacing={2}>
                    <img width={32}
                         height={32}
                         src={"/logo1.png"}/>
                    <Typography variant="h6"
                                component="div"
                                sx={{flexGrow: 1,}}>
                        ITTAAI
                    </Typography>
                </Stack>
            </Toolbar>
        </AppBar>
    )
}

export default Header