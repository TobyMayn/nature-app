import MapView from "./components/map";
import { SignIn } from "./components/sign-in";
import ButtonAppBar from "./components/topAppBar";

export default function Home() {
  return (
    <div>
      <ButtonAppBar></ButtonAppBar>
      <div className="">
        <SignIn></SignIn>
      </div>
      <MapView></MapView>
    </div>
  );
}
