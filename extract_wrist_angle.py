#extract_wrist_angle.py
import os
import argparse
import csv
import sys

# --- Required: your local loader ---
from load_mvnx import load_mvnx
#el environment en el que esta matplotlib es 3.13.5 (base)
file_name = "/Users/adriananietocarrasco/Documents/Python IMU/SUBJECT 3/SESSION 1/XSens output/20240227_subject_03_cond_ASS-POST-EXT_run_01.mvnx"
mvnx_file = load_mvnx(file_name)
# Optional fallback: relative orientation (needs SciPy if joint angles missing)
try:
    from scipy.spatial.transform import Rotation as R
    SCIPY_OK = True
except Exception:
    SCIPY_OK = False

def write_csv(path, rows, header):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)

def extract_joint_wrist(frames, axis_index=0, joint_key='jRightWrist'):
    """Extract wrist joint angle from ergonomic joint data (XZY)."""
    angles = []
    times = []
    missing = 0
    for fr in frames:
        t = fr.get('time', None)
        jd = fr.get('ergo_joint_data_xzy') or fr.get('ergo_joint_data')
        if jd and joint_key in jd:
            vec = jd[joint_key]
            if axis_index < 0 or axis_index > 2:
                raise ValueError("axis_index must be 0, 1, or 2 for XZY components.")
            angles.append(vec[axis_index])
            times.append(t)
        else:
            missing += 1
    if not angles:
        raise RuntimeError("No wrist joint angles found in frames (ergo_joint_data_xzy / ergo_joint_data).")
    return times, angles, missing

def extract_relative_wrist(frames, axis='x', hand='RightHand', forearm='RightForeArm', euler_order='XZY'):
    """
    Fallback: compute wrist joint angle as relative orientation (Hand wrt ForeArm),
    then take Euler component along the flex-ext axis (default 'X' in XZY).
    Requires SciPy.
    """
    if not SCIPY_OK:
        raise RuntimeError("SciPy not available; cannot compute relative orientation fallback.")

    idx_map = {'x': 0, 'y': 1, 'z': 2}
    axis = axis.lower()
    if axis not in idx_map:
        raise ValueError("axis must be one of 'x','y','z'")

    comp_idx = idx_map[axis]
    times, angles = [], []
    missing = 0

    for fr in frames:
        t = fr.get('time', None)
        seg = fr.get('segment_data', {})
        if hand in seg and forearm in seg:
            # segment 'ori' expected as 4D (w,x,y,z)
            qh = seg[hand].get('ori', None)
            qf = seg[forearm].get('ori', None)
            if qh is None or qf is None or len(qh) != 4 or len(qf) != 4:
                missing += 1
                continue
            # Relative orientation: forearm->hand
            # Xsens orientation is often given as quaternion (w, x, y, z)
            # SciPy expects (x, y, z, w)
            qh_xyzw = [qh[1], qh[2], qh[3], qh[0]]
            qf_xyzw = [qf[1], qf[2], qf[3], qf[0]]

            Rh = R.from_quat(qh_xyzw)
            Rf = R.from_quat(qf_xyzw)
            R_rel = Rf.inv() * Rh

            # Convert to Euler; default 'XZY' to match your ergonomic order
            euler = R_rel.as_euler(euler_order.lower())  # returns (x, z, y) in radians for 'xzy'
            times.append(t)
            angles.append(euler[comp_idx])
        else:
            missing += 1

    if not angles:
        raise RuntimeError("Could not compute relative wrist angle; missing segment orientations.")
    return times, angles, missing




def main(mvnx_file,
         axis_index=0,
         joint_key="jRightWrist",
         out_csv=None,
         fallback_relative=False,
         fallback_axis="x",
         fallback_euler_order="XZY"):
        ap = argparse.ArgumentParser(description="Extract wrist joint angle from MVNX and save to CSV.")
        ap.add_argument("--mvnx_file", required=True, type=str,
                        help="Path to .mvnx file")
        ap.add_argument("--axis_index", type=int, default=0,
                        help="Axis index for ergo joint angle (XZY order): 0=X (flex-ext), 1=Z, 2=Y")
        ap.add_argument("--joint_key", type=str, default="jRightWrist",
                        help="Joint name key (default jRightWrist)")
        ap.add_argument("--out_csv", type=str, default=None,
                        help="Output CSV path (default: <mvnx_basename>_wrist_angle.csv)")
        ap.add_argument("--fallback_relative", action="store_true",
                        help="If joint angles missing, compute relative (RightHand vs RightForeArm) using quaternions (SciPy).")
        ap.add_argument("--fallback_axis", type=str, default="x",
                        help="Fallback Euler axis to take from relative orientation (x/y/z). Default x (flex-ext).")
        ap.add_argument("--fallback_euler_order", type=str, default="XZY",
                        help="Euler order for fallback conversion (default XZY to match ergonomic).")
        args = ap.parse_args()

        if not os.path.isfile(args.mvnx_file):
            print(f"File not found: {args.mvnx_file}", file=sys.stderr)
            sys.exit(1)

        mvnx = load_mvnx(args.mvnx_file)
        frames = mvnx.file_data.get('frames', {}).get('frames', None) or mvnx.file_data.get('frames', None)

        # Some loaders store frames as a list directly; others under a key. Normalize:
        if isinstance(frames, dict) and 'frames' in frames:
            frames = frames['frames']
        if not isinstance(frames, list):
            raise RuntimeError("Unexpected frames structure; expected a list of per-frame dicts.")

        # Try ergonomic joint angles first
        try:
            t, ang, missing = extract_joint_wrist(frames,
                                                axis_index=args.axis_index,
                                                joint_key=args.joint_key)
            source = f"ergo_joint_data_xzy[{args.joint_key}][{args.axis_index}]"
            print(f"Extracted {len(ang)} wrist-angle samples from {source}. Missing frames: {missing}")
        except Exception as e:
            if args.fallback_relative:
                print(f"Primary extraction failed ({e}). Trying relative orientation fallback...")
                t, ang, missing = extract_relative_wrist(frames,
                                                        axis=args.fallback_axis,
                                                        hand='RightHand',
                                                        forearm='RightForeArm',
                                                        euler_order=args.fallback_euler_order)
                source = f"relative({args.fallback_euler_order}) RightHand vs RightForeArm axis={args.fallback_axis}"
                print(f"Extracted {len(ang)} wrist-angle samples from {source}. Missing frames: {missing}")
            else:
                raise

        # Build time vector if 'time' missing: use sample_rate from metadata
        if any(tt is None for tt in t):
            sr = mvnx.file_data.get('meta_data', {}).get('sample_rate', None)
            if sr:
                n = len(ang)
                t = [i / float(sr) for i in range(n)]
                print(f"Frame times not present; synthesized time vector at {sr} Hz.")
            else:
                # last resort: index as time
                n = len(ang)
                t = list(range(n))
                print("Frame times and sample_rate missing; writing index as time.")

        out_csv = args.out_csv or (os.path.splitext(args.mvnx_file)[0] + "_wrist_angle.csv")
        rows = list(zip(t, ang))
        write_csv(out_csv, rows, header=["time_s", "wrist_angle_rad"])

        print(f"✅ Saved wrist angle to: {out_csv}")
        print(f"   Source: {source}")



def cli():
    import argparse, os, sys
    ap = argparse.ArgumentParser(description="Extract wrist joint angle from MVNX and save to CSV.")
    ap.add_argument("--mvnx_file", required=True, type=str)
    ap.add_argument("--axis_index", type=int, default=0)
    ap.add_argument("--joint_key", type=str, default="jRightWrist")
    ap.add_argument("--out_csv", type=str, default=None)
    ap.add_argument("--fallback_relative", action="store_true")
    ap.add_argument("--fallback_axis", type=str, default="x")
    ap.add_argument("--fallback_euler_order", type=str, default="XZY")
    args = ap.parse_args()
    main(args.mvnx_file, args.axis_index, args.joint_key, args.out_csv,
         args.fallback_relative, args.fallback_axis, args.fallback_euler_order)

if __name__ == "__main__":
    cli()


if __name__ == '__main__':

    # Program entry point
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--mvnx_file', 
        required=False, 
        type=str, 
        default=("/Users/adriananietocarrasco/Documents/Python IMU/SUBJECT 3/SESSION 1/XSens output/"
                 "20240227_subject_03_cond_ASS-POST-EXT_run_01.mvnx"),
        help='The MVNX file to load (defaults to ASS-POST-EXT run 01)'
    )
    args = parser.parse_args()

    try:
        main(args.mvnx_file)
    except Exception as e:
        print("Error: %s" % e)

