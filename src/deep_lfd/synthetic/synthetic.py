class Synthetic:

    def __init__(self, translate_options, rotate_options, reflection_options, bounds):

        self.translate_step = translate_options[0]
        self.max_num_translations = translate_options[1]

        self.rotate_range = rotate_options[0] % 180
        self.rotate_step = rotate_options[1]
        self.max_num_rotations = rotate_options[2]

    def apply_rotations(data):
        """
        input/output data are lists of format (image, label)
        """

        results = np.array([])

        for img, label in data:

            curr = np.array([(img, label)])

            for degree_shift in np.linspace(-self.rotate_range, self.rotate_range, num = self.rotate_step):
                new_img = img.transform(np.array([0,0]),np.deg2rad(degree_shift))

                M = cv2.getRotationMatrix2D((img.center[0], img.center[1]), degree_shift, 1)
                new_xy = np.matmul(M, np.array([label[0], label[1], 1]))
                new_theta = np.array([label[2] - degree_shift])
                new_depth = np.array(label[3])
                new_label = np.append(new_xy, new_theta, new_depth)

                if check_bounds(new_label):
                    curr = np.append(curr, (new_img, new_label)))

                if len(curr) >= self.max_num_rotations:
                    break

            results = np.append(results, curr)

        return results

    def apply_translations(data):
        """
        input/output data are lists of format (image, label)
        """

        results = np.array([])

        for img, label in data:

            curr = np.array([img, label])

            for x in range(lo, hi):
                for y in range(lo, hi):

                    if check_bounds(new_label):
                        curr = np.append(curr, (new_img, new_label)))

                    if len(curr) >= self.max_num_translations:
                        break

            results = np.append(results, curr)

        return results

    def apply_reflections(data):
        """
        input/output data are lists of format (image, label)
        """

        results = np.array([])

        for img, label in data:
            new_img = cv2.flip(img, 1)
            new_label = [len(new_img[0]) - label[0], label[1], label[2], label[3]]

            if check_bounds(new_label):
                results = np.append(results, (new_img, new_label))

        return results
    def apply_filters(data):

        if()
            data = self.apply_rotations(data)
        elif:
            data = self.apply_translations(data)


    def check_bounds(label):
        b_l = self.bounds[0]
        b_u = self.bounds[1]
        b_r = self.bounds[2]
        c_bounds = np.array([[b_l[0], b_u[0]], [b_l[1], b_u[1]], b_r)

        for coord in range(3):
            if not (c_bounds[i][0] <= label[i] and c_bounds[i][1] >= label[i]):
                return False

        return True
