import { AuthGuard } from "../components/auth-guard";
import MapView from "../components/map";
import ButtonAppBar from "../components/topAppBar";

export default function MapPage() {
  return (
    <AuthGuard>
      <div>
        <ButtonAppBar />
        <MapView />
      </div>
    </AuthGuard>
  );
}