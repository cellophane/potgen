from starlette.applications import Starlette
import uvicorn
from starlette.responses import FileResponse
from potgen import PotGen
from starlette.responses import JSONResponse, HTMLResponse, RedirectResponse
import ast
from scipy.interpolate import UnivariateSpline
app = Starlette(debug=True)


@app.route("/")
def form(request):
    return HTMLResponse("""
        <h3>Generate your own 3D-printable pot!<h3>
        <form action="generate" enctype="multipart/form-data">
            parameters for the profile: x values must be increasing.
            x values:
            <input type="text" name="x" value="[0,5,7,8,12]">
            y values:
            <input type="text" name="y" value = "[2,3,1.75,1.5,3]">
            resolution [zRes,thetaRes]:
            <input type="text" name="res" value = "[16,4]">
            <input type="submit" value="create pot!">
        </form>
        
    """)

@app.route("/generate")
def generate(request):
    xString = request.query_params['x']
    yString = request.query_params['y']
    resString = request.query_params['res']
    x = ast.literal_eval(xString)
    y = ast.literal_eval(yString)
    res = ast.literal_eval(resString)
    curve = UnivariateSpline(x, y)
    if res[0]*res[1]>10**5:
        return HTMLResponse("this would be too big.")
    pot = PotGen(curve,res)
    pot.generate()
    pot.save()
    
    return FileResponse('pot.stl',filename = 'pot.stl')

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5225)