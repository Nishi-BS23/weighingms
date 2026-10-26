import { useCallback, useState } from "react";
import { api } from "./api/client";
import type { Batch, Operator, Session, SimulationKind } from "./api/types";
import { BatchQueueScreen } from "./features/batch-queue/BatchQueueScreen";
import { OperatorDialog } from "./features/chrome/OperatorDialog";
import { StatusStrip } from "./features/chrome/StatusStrip";
import { type Step, StepIndicator } from "./features/chrome/StepIndicator";
import { TopBar } from "./features/chrome/TopBar";
import { SimulationControls, TrainingPanel } from "./features/chrome/TrainingPanel";
import { DoneScreen } from "./features/ticket/DoneScreen";
import { WeighScreen } from "./features/weighing/WeighScreen";
import { ErrorBoundary } from "./shared/ErrorBoundary";
import { errorCode } from "./shared/messages";
import { usePolling } from "./shared/use-polling";
import { useResource } from "./shared/use-resource";

const DEVICE_POLL_MS = 1000;

export function App() {
  const [step, setStep] = useState<Step>("queue");
  const [session, setSession] = useState<Session | null>(null);
  const [operatorDialog, setOperatorDialog] = useState(false);
  const [signedIn, setSignedIn] = useState<Operator | null>(null);
  const currentOperator = useResource(() => api.currentOperator());
  const devices = usePolling((signal) => api.deviceStatus(signal), DEVICE_POLL_MS);
  const operator = signedIn ?? currentOperator.data ?? null;

  const onSelected = useCallback(async (batch: Batch) => {
    const started = await api.startSession(batch.batchId);
    setSession(started);
    setStep(started.status === "COMPLETED" ? "done" : "weigh");
  }, []);

  const onSessionChange = useCallback((updated: Session) => {
    setSession(updated);
    if (updated.status === "COMPLETED") setStep("done");
  }, []);

  const backToQueue = useCallback(() => {
    setSession(null);
    setStep("queue");
  }, []);

  // A training reset restores the seed and clears the operator: remount the queue so it reloads.
  const [resets, setResets] = useState(0);
  const reloadOperator = currentOperator.reload;
  const onTrainingReset = useCallback(() => {
    backToQueue();
    setSignedIn(null);
    reloadOperator();
    setResets((n) => n + 1);
  }, [backToQueue, reloadOperator]);

  const weighing =
    step === "weigh" && session?.status === "IN_PROGRESS" && session.activeComponentId !== null;
  const simulate = weighing
    ? async (kind: SimulationKind) => {
        await api.training.simulateActive(session.sessionId, kind);
      }
    : undefined;
  const resetWeighing = weighing
    ? async () => {
        await api.training.resetWeighing(session.sessionId);
      }
    : undefined;

  const backendDown = errorCode(devices.error) === "NETWORK_ERROR";

  return (
    <div className="wrap">
      <div className="controls">
        <StepIndicator
          current={step}
          reachable={{
            queue: true,
            weigh: session?.status === "IN_PROGRESS",
            done: session?.status === "COMPLETED",
          }}
          onSelect={(s) => (s === "queue" ? backToQueue() : setStep(s))}
        />
        <span className="spacer" />
        <SimulationControls onSimulate={simulate} onResetWeighing={resetWeighing} />
      </div>

      <div className="device">
        <div className="screen">
          <div>
            {backendDown && <div className="banner">Station service unavailable</div>}
            <TopBar
              stationName={devices.data?.stationName ?? "STATION 01"}
              batch={step === "queue" ? null : session}
              operator={operator}
              onOperatorClick={() => setOperatorDialog(true)}
            />
          </div>
          <ErrorBoundary key={`${step}-${resets}`} onBack={backToQueue}>
            {step === "queue" && <BatchQueueScreen onSelected={onSelected} />}
            {step === "weigh" && session && (
              <WeighScreen
                session={session}
                onSessionChange={onSessionChange}
                onQuit={backToQueue}
              />
            )}
            {step === "done" && session && (
              <DoneScreen
                session={session}
                onSessionChange={setSession}
                onNextBatch={backToQueue}
              />
            )}
          </ErrorBoundary>
          <StatusStrip status={devices.data} />
          {operatorDialog && (
            <OperatorDialog
              onCancel={() => setOperatorDialog(false)}
              onSignedIn={(op) => {
                setSignedIn(op);
                setOperatorDialog(false);
              }}
            />
          )}
        </div>
      </div>

      <TrainingPanel onTrainingReset={onTrainingReset} />
    </div>
  );
}
