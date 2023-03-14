data_df.to_csv("/Users/claricepark/SanchezLab/data/2023JAN18_maldi_dia_tims_ims.imzML", index=False)
return
contour_df = data_df.groupby(['mz', 'mobility'], as_index=False).aggregate(sum)
contour_df = contour_df[contour_df['intensity'] >= (np.max(contour_df['intensity']) * 0.0002)]
contour_df = contour_df.round({'mz': 4, 'mobility': 3})