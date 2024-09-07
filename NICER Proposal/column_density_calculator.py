import pandas as pd 
import argparse

def select_gal_nh(ra:float, dec:float) -> float:
	''' 
	Select RA and Dec of GRB and corresponding Galactic hydrogen column density (MW).
	Author: Joe Fisher (UCD)

	Inputs:	
	-------
	``ra``: float
		The RA of the source in degrees
	``dec``: float
		The Dec of the source in degrees

	Outputs:
	--------
	``gal_nh``: float
		The Galactic hydrogen column density in the direction of the source
	'''

	# Load NH skymap data
	nh_df=pd.read_csv('/data/user/fisher/_req_/nhi_hpx.dat', sep='\s+')
	nh_df.columns=['HPX index', 'RA', 'Dec', 'GLONG', 'GLAT', 'HI']
	#nh_df=nh_df[::2000]

	# Get rows of dataframe with selected RA and Dec
	nh_df_ra_dec = nh_df[ (nh_df['RA'].round(1) == round(ra, 1)) & (nh_df['Dec'].round(1) == round(dec, 1))]
	# Average NH from rows with selected RA and Dec
	gal_nh = nh_df_ra_dec['HI'].mean()

	return gal_nh

def main():
	# Parse arguments
    parser = argparse.ArgumentParser(description='Select Galactic NH for a given RA and Dec')
    parser.add_argument('ra', type=float, help='RA of the source in degrees')
    parser.add_argument('dec', type=float, help='Dec of the source in degrees')
    args = parser.parse_args()

    # Select Galactic NH
    gal_nh = select_gal_nh(args.ra, args.dec)
    print(f'Galactic NH = {gal_nh}')

if __name__ == '__main__':
    main()